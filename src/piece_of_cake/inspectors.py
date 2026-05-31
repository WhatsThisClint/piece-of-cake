"""Layer profiling helpers for unknown custom data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .io import require_geopandas, require_rasterio


def inspect_raster(path: str | Path, *, band: int = 1, max_unique: int = 32) -> dict[str, Any]:
    """Inspect a raster and suggest a styling family."""

    rasterio, *_ = require_rasterio()
    path = Path(path)
    with rasterio.open(path) as src:
        sample = src.read(
            band,
            out_shape=(min(src.height, 256), min(src.width, 256)),
            masked=True,
        )
        values = np.asarray(sample.compressed())
        unique = np.unique(values)
        many_unique = len(unique) > max_unique
        numeric = np.issubdtype(values.dtype, np.number)
        if numeric and many_unique:
            suggestion = "continuous"
        elif len(unique) <= max_unique:
            suggestion = "categorical"
        else:
            suggestion = "continuous"
        return {
            "path": str(path),
            "kind": "raster",
            "crs": str(src.crs),
            "width": src.width,
            "height": src.height,
            "dtype": str(src.dtypes[band - 1]),
            "nodata": src.nodata,
            "value_min": float(values.min()) if values.size and numeric else None,
            "value_max": float(values.max()) if values.size and numeric else None,
            "unique_count_sample": int(len(unique)),
            "unique_values_sample": unique[:max_unique].tolist(),
            "suggested_style": suggestion,
        }


def inspect_vector(path: str | Path, *, layer: str | None = None, max_unique: int = 24) -> dict[str, Any]:
    """Inspect vector columns and suggest useful color/label fields."""

    gpd = require_geopandas()
    path = Path(path)
    gdf = gpd.read_file(path, layer=layer) if layer else gpd.read_file(path)
    columns = []
    color_by: list[str] = []
    label_by: list[str] = []
    hover_fields: list[str] = []

    for column in gdf.columns:
        if column == gdf.geometry.name:
            continue
        series = gdf[column].dropna()
        dtype = str(series.dtype)
        unique_count = int(series.nunique()) if len(series) else 0
        lower = column.lower()
        numeric = np.issubdtype(series.dtype, np.number) if len(series) else False
        if numeric:
            role = "continuous" if unique_count > max_unique else "categorical"
            color_by.append(column)
        elif unique_count <= max_unique and any(k in lower for k in ("class", "type", "status", "risk")):
            role = "categorical"
            color_by.append(column)
        elif any(k in lower for k in ("name", "village", "id", "label")):
            role = "label"
            label_by.append(column)
        else:
            role = "hover"
        if len(hover_fields) < 8:
            hover_fields.append(column)
        columns.append(
            {
                "name": column,
                "dtype": dtype,
                "unique_count": unique_count,
                "sample_values": series.astype(str).unique()[:max_unique].tolist(),
                "suggested_role": role,
            }
        )

    return {
        "path": str(path),
        "kind": "vector",
        "layer": layer,
        "crs": str(gdf.crs),
        "geometry_types": sorted(set(gdf.geometry.geom_type.dropna().astype(str))),
        "feature_count": int(len(gdf)),
        "columns": columns,
        "suggested_columns": {
            "color_by": color_by,
            "label_by": label_by,
            "hover_fields": hover_fields,
        },
    }

