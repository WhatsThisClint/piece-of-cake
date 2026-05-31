"""Style profiles for unknown, custom, and known geospatial layers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np


DEFAULT_CATEGORICAL_COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]


@dataclass
class StyleProfile:
    """A render style for rasters or vectors.

    ``kind`` is one of ``continuous``, ``categorical``, or ``single``.
    ``classes`` maps raster/vector values to ``{"label": str, "color": hex}``.
    """

    kind: str = "continuous"
    label: str | None = None
    cmap: str = "Viridis"
    opacity: float = 0.72
    classes: dict[Any, dict[str, str]] = field(default_factory=dict)
    color: str = "#2563eb"
    outline: str = "#111827"
    legend: bool = True

    @classmethod
    def from_value(cls, value: "StyleProfile | Mapping[str, Any] | str | None") -> "StyleProfile":
        if isinstance(value, StyleProfile):
            return value
        if value is None:
            return cls()
        if isinstance(value, str):
            return built_in_style(value)
        data = dict(value)
        kind = data.pop("type", data.pop("kind", "continuous"))
        return cls(kind=kind, **data)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.kind,
            "label": self.label,
            "cmap": self.cmap,
            "opacity": self.opacity,
            "classes": self.classes,
            "color": self.color,
            "outline": self.outline,
            "legend": self.legend,
        }


BUILTIN_STYLES: dict[str, StyleProfile] = {
    "dem": StyleProfile(kind="continuous", label="Elevation", cmap="Earth", opacity=1.0),
    "continuous": StyleProfile(kind="continuous", cmap="Viridis", opacity=0.72),
    "tree_canopy": StyleProfile(kind="continuous", label="Tree canopy", cmap="Greens", opacity=0.65),
    "ndvi": StyleProfile(kind="continuous", label="NDVI", cmap="Greens", opacity=0.65),
    "risk": StyleProfile(
        kind="categorical",
        opacity=0.70,
        classes={
            1: {"label": "Low", "color": "#2ca25f"},
            2: {"label": "Medium", "color": "#fee08b"},
            3: {"label": "High", "color": "#de2d26"},
        },
    ),
    "indiasat_lulc": StyleProfile(
        kind="categorical",
        opacity=0.70,
        classes={
            1: {"label": "Built up", "color": "#ff0000"},
            2: {"label": "Kharif water", "color": "#74ccf4"},
            3: {"label": "Kharif and rabi water", "color": "#1ca3ec"},
            4: {"label": "Kharif/Rabi/Zaid water", "color": "#0f5e9c"},
            6: {"label": "Trees", "color": "#38761d"},
            7: {"label": "Barren land", "color": "#a9a9a9"},
            8: {"label": "Single Kharif cropping", "color": "#bad93e"},
            9: {"label": "Single non-kharif", "color": "#f59d22"},
            10: {"label": "Double cropping", "color": "#ff9371"},
            11: {"label": "Triple/annual cropping", "color": "#b3561d"},
            12: {"label": "Shrubs and scrubs", "color": "#a9a9a9"},
        },
    ),
    "esa_worldcover": StyleProfile(
        kind="categorical",
        opacity=0.70,
        classes={
            10: {"label": "Tree cover", "color": "#006400"},
            20: {"label": "Shrubland", "color": "#ffbb22"},
            30: {"label": "Grassland", "color": "#ffff4c"},
            40: {"label": "Cropland", "color": "#f096ff"},
            50: {"label": "Built-up", "color": "#fa0000"},
            60: {"label": "Bare/sparse vegetation", "color": "#b4b4b4"},
            70: {"label": "Snow and ice", "color": "#f0f0f0"},
            80: {"label": "Permanent water bodies", "color": "#0064c8"},
            90: {"label": "Herbaceous wetland", "color": "#0096a0"},
            95: {"label": "Mangroves", "color": "#00cf75"},
            100: {"label": "Moss and lichen", "color": "#fae6a0"},
        },
    ),
}


def list_builtin_styles() -> list[str]:
    return sorted(BUILTIN_STYLES)


def built_in_style(name: str) -> StyleProfile:
    try:
        profile = BUILTIN_STYLES[name]
    except KeyError as exc:
        known = ", ".join(list_builtin_styles())
        raise ValueError(f"Unknown style {name!r}. Built-in styles: {known}") from exc
    return StyleProfile.from_value(profile.to_dict())


def auto_style(values: np.ndarray | list[Any], *, max_categories: int = 16) -> StyleProfile:
    """Suggest a generic style from data values.

    This is intentionally conservative: if a layer has many unique numeric
    values, it is treated as continuous. If it has a small number of values, it
    is styled categorically with placeholder labels.
    """

    arr = np.asarray(values)
    arr = arr[np.isfinite(arr)] if np.issubdtype(arr.dtype, np.number) else arr
    unique = np.unique(arr)
    if 0 < len(unique) <= max_categories:
        classes = {}
        for idx, value in enumerate(unique.tolist()):
            classes[value] = {
                "label": f"Class {value}",
                "color": DEFAULT_CATEGORICAL_COLORS[idx % len(DEFAULT_CATEGORICAL_COLORS)],
            }
        return StyleProfile(kind="categorical", classes=classes)
    return StyleProfile(kind="continuous", cmap="Viridis")


def categorical_colorscale(profile: StyleProfile) -> tuple[list[list[Any]], dict[Any, int]]:
    """Convert class colors into a Plotly colorscale and value index map."""

    classes = profile.classes or {}
    if not classes:
        return [[0.0, "#cccccc"], [1.0, "#cccccc"]], {}

    value_map = {value: idx for idx, value in enumerate(classes)}
    max_idx = max(len(value_map) - 1, 1)
    colorscale = []
    for value, idx in value_map.items():
        color = classes[value].get("color", DEFAULT_CATEGORICAL_COLORS[idx % len(DEFAULT_CATEGORICAL_COLORS)])
        position = idx / max_idx
        colorscale.append([position, color])
    return colorscale, value_map

