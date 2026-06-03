"""DEM provider registry and source configuration helpers."""

from __future__ import annotations

import hashlib
import getpass
import json
import os
import re
import shutil
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, TypeAlias

import numpy as np

from .bounds import Bounds
from .io import read_raster_grid


class DemProvider(Protocol):
    """Protocol for DEM download/provider integrations."""

    def fetch_dem(self, bounds: Bounds, *, width: int, height: int) -> tuple[np.ndarray, Bounds]:
        """Return ``(dem_array, bounds)`` for the requested WGS84 bounds."""


Downloader = Callable[[str, Path, Mapping[str, str], float], None]

_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
_KNOWN_PROVIDERS = {"local", "opentopography", "url"}


@dataclass(frozen=True)
class SourcesConfig:
    """Loaded source/account configuration.

    ``base_dir`` is used to resolve relative paths from YAML/JSON config files.
    """

    data: Mapping[str, Any]
    base_dir: Path | None = None


ConfigInput: TypeAlias = str | Path | Mapping[str, Any] | SourcesConfig | None


@dataclass
class LocalRasterProvider:
    """Read a local DEM raster and clip/resample it to the requested bounds."""

    path: str | Path

    def fetch_dem(self, bounds: Bounds, *, width: int, height: int) -> tuple[np.ndarray, Bounds]:
        return read_raster_grid(self.path, bounds=bounds, width=width, height=height)


@dataclass
class UrlRasterProvider:
    """Download a GeoTIFF from a URL, then clip/resample it locally.

    The URL may include Python format placeholders such as ``{south}``,
    ``{north}``, ``{west}``, and ``{east}``.
    """

    url: str
    cache_dir: str | Path | None = None
    headers: Mapping[str, str] | None = None
    timeout: float = 120.0
    downloader: Downloader = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.downloader is None:
            self.downloader = _download_url

    def fetch_dem(self, bounds: Bounds, *, width: int, height: int) -> tuple[np.ndarray, Bounds]:
        url = self._format_url(bounds)
        path = _cached_path(
            provider="url",
            cache_dir=self.cache_dir,
            key=url,
            suffix=".tif",
        )
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            self.downloader(url, path, self.headers or {}, self.timeout)
        return read_raster_grid(path, bounds=bounds, width=width, height=height)

    def _format_url(self, bounds: Bounds) -> str:
        values = {
            "south": bounds.min_lat,
            "north": bounds.max_lat,
            "west": bounds.min_lon,
            "east": bounds.max_lon,
            "min_lon": bounds.min_lon,
            "min_lat": bounds.min_lat,
            "max_lon": bounds.max_lon,
            "max_lat": bounds.max_lat,
        }
        return self.url.format(**values)


@dataclass
class OpenTopographyProvider:
    """Fetch clipped DEM GeoTIFFs from the OpenTopography Global DEM API."""

    dem_type: str = "SRTMGL1"
    api_key: str | None = None
    api_url: str = "https://portal.opentopography.org/API/globaldem"
    output_format: str = "GTiff"
    cache_dir: str | Path | None = None
    timeout: float = 120.0
    extra_params: Mapping[str, Any] | None = None
    headers: Mapping[str, str] | None = None
    downloader: Downloader = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.downloader is None:
            self.downloader = _download_url
        if self.api_key is None:
            self.api_key = os.environ.get("OPENTOPOGRAPHY_API_KEY")

    @classmethod
    def from_settings(
        cls,
        settings: Mapping[str, Any],
        *,
        base_dir: Path | None = None,
    ) -> "OpenTopographyProvider":
        api_key = settings.get("api_key")
        api_key_env = settings.get("api_key_env")
        if not api_key and api_key_env:
            api_key = os.environ.get(str(api_key_env))
        cache_dir = _resolve_path(settings.get("cache_dir"), base_dir)
        return cls(
            dem_type=str(settings.get("dem_type") or settings.get("demtype") or "SRTMGL1"),
            api_key=str(api_key) if api_key else None,
            api_url=str(settings.get("api_url") or "https://portal.opentopography.org/API/globaldem"),
            output_format=str(settings.get("output_format") or settings.get("outputFormat") or "GTiff"),
            cache_dir=cache_dir,
            timeout=float(settings.get("timeout", 120.0)),
            extra_params=settings.get("params") or None,
            headers=settings.get("headers") or None,
        )

    def build_url(self, bounds: Bounds) -> str:
        params: dict[str, Any] = {
            "demtype": self.dem_type,
            "south": bounds.min_lat,
            "north": bounds.max_lat,
            "west": bounds.min_lon,
            "east": bounds.max_lon,
            "outputFormat": self.output_format,
        }
        if self.extra_params:
            params.update(self.extra_params)
        if self.api_key:
            params["API_Key"] = self.api_key
        return f"{self.api_url}?{urllib.parse.urlencode(params)}"

    def fetch_dem(self, bounds: Bounds, *, width: int, height: int) -> tuple[np.ndarray, Bounds]:
        url = self.build_url(bounds)
        path = _cached_path(
            provider="opentopography",
            cache_dir=self.cache_dir,
            key=url,
            suffix=".tif",
        )
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            self.downloader(url, path, self.headers or {}, self.timeout)
        return read_raster_grid(path, bounds=bounds, width=width, height=height)


def setup_opentopography_key(
    api_key: str | None = None,
    *,
    env_var: str = "OPENTOPOGRAPHY_API_KEY",
    prompt: str = "OpenTopography API key: ",
    overwrite: bool = False,
) -> bool:
    """Store an OpenTopography API key in the current Python session.

    This is intended for JupyterLab, Colab, and other notebook workflows. It
    checks whether ``env_var`` is already set, prompts with a hidden input only
    when needed, and stores the key in ``os.environ`` for the current Python
    process. It does not write the key to disk and does not return the key.
    """

    if os.environ.get(env_var) and not overwrite:
        return True

    key = api_key if api_key is not None else getpass.getpass(prompt)
    key = str(key).strip()
    if not key:
        raise ValueError("OpenTopography API key cannot be empty")
    os.environ[env_var] = key
    return True


def load_sources_config(config: ConfigInput) -> SourcesConfig:
    """Load YAML/JSON source configuration.

    YAML files require the optional ``providers`` extra because Python does not
    ship a YAML parser.
    """

    if config is None:
        return SourcesConfig(data={})
    if isinstance(config, SourcesConfig):
        return config
    if isinstance(config, Mapping):
        return SourcesConfig(data=_resolve_env(config))

    path = Path(config)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        raw = json.loads(text)
    else:
        try:
            import yaml
        except ImportError as exc:
            raise ImportError(
                "YAML source configs need PyYAML. Install with: "
                "pip install 'piece-of-cake-terrain[providers]'"
            ) from exc
        raw = yaml.safe_load(text)
    if raw is None:
        raw = {}
    if not isinstance(raw, Mapping):
        raise ValueError("source config must be a mapping at the top level")
    return SourcesConfig(data=_resolve_env(raw), base_dir=path.parent)


def build_dem_provider(source: str | None = "auto", *, config: ConfigInput = None) -> DemProvider:
    """Build a DEM provider from a source name and optional YAML/JSON config."""

    sources_config = load_sources_config(config)
    source_name = source or "auto"
    source_entry = _select_source_entry(source_name, sources_config.data)
    provider_name = str(source_entry.get("provider") or source_name)
    if provider_name == "auto":
        provider_name = "opentopography"

    account_entry = _select_account_entry(provider_name, source_entry, sources_config.data)
    settings = {**account_entry, **source_entry}
    settings.pop("provider", None)
    settings.pop("account", None)

    if provider_name == "opentopography":
        return OpenTopographyProvider.from_settings(settings, base_dir=sources_config.base_dir)
    if provider_name == "local":
        path = settings.get("path")
        if not path:
            raise ValueError("local DEM sources need a path")
        return LocalRasterProvider(path=_resolve_path(path, sources_config.base_dir))
    if provider_name == "url":
        url = settings.get("url")
        if not url:
            raise ValueError("url DEM sources need a url")
        return UrlRasterProvider(
            url=str(url),
            cache_dir=_resolve_path(settings.get("cache_dir"), sources_config.base_dir),
            headers=settings.get("headers") or None,
            timeout=float(settings.get("timeout", 120.0)),
        )

    raise ValueError(f"Unknown DEM provider {provider_name!r}")


def _select_source_entry(source_name: str, data: Mapping[str, Any]) -> dict[str, Any]:
    sources = data.get("sources") or {}
    if not isinstance(sources, Mapping):
        raise ValueError("config field 'sources' must be a mapping")

    if source_name == "auto":
        default_dem = data.get("default_dem") or data.get("default_source")
        if isinstance(default_dem, Mapping):
            return dict(default_dem)
        if default_dem:
            source_name = str(default_dem)
        else:
            return {"provider": "opentopography"}

    if source_name in sources:
        value = sources[source_name]
        if isinstance(value, Mapping):
            return dict(value)
        if isinstance(value, str):
            return {"provider": value}
        raise ValueError(f"source {source_name!r} must be a mapping or provider name")

    if source_name in _KNOWN_PROVIDERS:
        return {"provider": source_name}

    raise ValueError(f"Source {source_name!r} was not found in the source config")


def _select_account_entry(
    provider_name: str,
    source_entry: Mapping[str, Any],
    data: Mapping[str, Any],
) -> dict[str, Any]:
    accounts = data.get("accounts") or {}
    if not isinstance(accounts, Mapping):
        raise ValueError("config field 'accounts' must be a mapping")

    account_name = source_entry.get("account", provider_name)
    if not account_name:
        return {}
    account = accounts.get(str(account_name), {})
    if account is None:
        return {}
    if not isinstance(account, Mapping):
        raise ValueError(f"account {account_name!r} must be a mapping")
    return dict(account)


def _cached_path(
    *,
    provider: str,
    cache_dir: str | Path | None,
    key: str,
    suffix: str,
) -> Path:
    root = Path(cache_dir) if cache_dir else _default_cache_dir()
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]
    return root / provider / f"{digest}{suffix}"


def _default_cache_dir() -> Path:
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "piece-of-cake" / "cache"
    return Path.home() / ".cache" / "piece-of-cake"


def _download_url(url: str, path: Path, headers: Mapping[str, str], timeout: float) -> None:
    request = urllib.request.Request(url, headers=dict(headers))
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get("content-type", "").lower()
            first_chunk = response.read(512)
            if _looks_like_error_response(first_chunk, content_type):
                snippet = first_chunk.decode("utf-8", errors="replace").strip()
                raise RuntimeError(f"DEM provider returned a non-raster response: {snippet[:300]}")
            with tmp_path.open("wb") as handle:
                handle.write(first_chunk)
                shutil.copyfileobj(response, handle)
        tmp_path.replace(path)
    except urllib.error.URLError as exc:
        if tmp_path.exists():
            tmp_path.unlink()
        raise RuntimeError(f"Could not download DEM from {url}: {exc}") from exc


def _looks_like_error_response(first_chunk: bytes, content_type: str) -> bool:
    stripped = first_chunk.lstrip()
    if content_type.startswith("text/") or "json" in content_type or "xml" in content_type:
        return True
    return stripped.startswith((b"{", b"[", b"<html", b"<!DOCTYPE", b"<?xml"))


def _resolve_path(value: Any, base_dir: Path | None) -> str | Path | None:
    if value in (None, ""):
        return None
    path = Path(str(value))
    if base_dir and not path.is_absolute():
        return base_dir / path
    return path


def _resolve_env(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _resolve_env(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve_env(item) for item in value]
    if isinstance(value, str):
        return _ENV_PATTERN.sub(lambda match: os.environ.get(match.group(1), ""), value)
    return value
