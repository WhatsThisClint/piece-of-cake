import os
from pathlib import Path

import numpy as np

from piece_of_cake import (
    EsaWorldCoverProvider,
    OpenTopographyProvider,
    TerrainScene,
    build_dem_provider,
    load_sources_config,
    setup_opentopography_key,
    worldcover_tiles,
)
from piece_of_cake.bounds import Bounds
from piece_of_cake.io import require_rasterio


def test_local_dem_source_from_yaml_config(tmp_path):
    dem_path = tmp_path / "dem.tif"
    _write_test_dem(dem_path)
    config_path = tmp_path / "sources.yml"
    config_path.write_text(
        """
default_dem: local_dem
sources:
  local_dem:
    provider: local
    path: dem.tif
""".strip(),
        encoding="utf-8",
    )

    scene = TerrainScene.from_bbox(76.0, 18.0, 76.1, 18.1)
    scene.add_dem(source="auto", config=config_path, width=4, height=2)

    assert scene.dem.shape == (2, 4)
    assert scene.bounds == Bounds(76.0, 18.0, 76.1, 18.1)
    assert np.isfinite(scene.dem).all()


def test_build_dem_provider_uses_account_env(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENTOPOGRAPHY_API_KEY", "from-env")
    config = load_sources_config(
        {
            "accounts": {"opentopography": {"api_key_env": "OPENTOPOGRAPHY_API_KEY"}},
            "sources": {
                "cop30": {
                    "provider": "opentopography",
                    "dem_type": "COP30",
                    "cache_dir": str(tmp_path / "cache"),
                }
            },
        }
    )

    provider = build_dem_provider("cop30", config=config)

    assert isinstance(provider, OpenTopographyProvider)
    assert provider.dem_type == "COP30"
    assert provider.api_key == "from-env"


def test_opentopography_provider_downloads_and_caches(tmp_path):
    dem_path = tmp_path / "served.tif"
    _write_test_dem(dem_path)
    requested_urls = []

    def fake_download(url: str, path: Path, headers, timeout: float) -> None:
        requested_urls.append(url)
        path.write_bytes(dem_path.read_bytes())

    provider = OpenTopographyProvider(
        dem_type="COP30",
        api_key="secret",
        cache_dir=tmp_path / "cache",
        downloader=fake_download,
        timeout=5,
    )

    bounds = Bounds(76.0, 18.0, 76.1, 18.1)
    dem, fetched_bounds = provider.fetch_dem(bounds, width=3, height=3)
    dem_again, _ = provider.fetch_dem(bounds, width=3, height=3)

    assert dem.shape == (3, 3)
    assert np.array_equal(dem, dem_again)
    assert fetched_bounds == bounds
    assert len(requested_urls) == 1
    assert "demtype=COP30" in requested_urls[0]
    assert "south=18.0" in requested_urls[0]
    assert "north=18.1" in requested_urls[0]
    assert "west=76.0" in requested_urls[0]
    assert "east=76.1" in requested_urls[0]
    assert "API_Key=secret" in requested_urls[0]


def test_worldcover_tiles_for_mumbai_bbox():
    bounds = Bounds(72.78, 18.88, 73.05, 19.30)

    assert worldcover_tiles(bounds) == ["N18E072"]


def test_worldcover_tiles_cross_boundaries():
    bounds = Bounds(71.9, 17.9, 75.2, 21.1)

    assert worldcover_tiles(bounds) == [
        "N15E069",
        "N15E072",
        "N15E075",
        "N18E069",
        "N18E072",
        "N18E075",
        "N21E069",
        "N21E072",
        "N21E075",
    ]


def test_worldcover_provider_resolves_latest_and_urls():
    provider = EsaWorldCoverProvider()

    assert provider.year == "2021"
    assert provider.version == "200"
    assert provider.tile_urls(Bounds(72.78, 18.88, 73.05, 19.30)) == [
        (
            "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
            "ESA_WorldCover_10m_2021_v200_N18E072_Map.tif"
        )
    ]


def test_setup_opentopography_key_uses_existing_env_without_prompt(monkeypatch):
    monkeypatch.setenv("OPENTOPOGRAPHY_API_KEY", "already-set")

    def fail_prompt(prompt: str) -> str:
        raise AssertionError("prompt should not be called when key already exists")

    monkeypatch.setattr("piece_of_cake.providers.getpass.getpass", fail_prompt)

    assert setup_opentopography_key() is True
    assert os.environ["OPENTOPOGRAPHY_API_KEY"] == "already-set"


def test_setup_opentopography_key_prompts_and_stores_session_env(monkeypatch):
    monkeypatch.delenv("OPENTOPOGRAPHY_API_KEY", raising=False)
    prompts = []

    def fake_prompt(prompt: str) -> str:
        prompts.append(prompt)
        return " secret "

    monkeypatch.setattr("piece_of_cake.providers.getpass.getpass", fake_prompt)

    assert setup_opentopography_key() is True
    assert os.environ["OPENTOPOGRAPHY_API_KEY"] == "secret"
    assert "https://portal.opentopography.org/myopentopo" in prompts[0]
    assert "Get an API Key" in prompts[0]


def test_setup_opentopography_key_rejects_empty_key(monkeypatch):
    monkeypatch.delenv("OPENTOPOGRAPHY_API_KEY", raising=False)
    monkeypatch.setattr("piece_of_cake.providers.getpass.getpass", lambda prompt: " ")

    try:
        setup_opentopography_key()
    except ValueError as exc:
        assert "cannot be empty" in str(exc)
    else:
        raise AssertionError("empty API key should fail")


def _write_test_dem(path: Path) -> None:
    rasterio, from_bounds, *_ = require_rasterio()
    values = np.array(
        [
            [10, 20, 30],
            [15, 25, 35],
            [20, 30, 40],
        ],
        dtype="float32",
    )
    transform = from_bounds(76.0, 18.0, 76.1, 18.1, values.shape[1], values.shape[0])
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=values.shape[0],
        width=values.shape[1],
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(values, 1)
