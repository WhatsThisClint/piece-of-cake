"""Raster and vector IO helpers.

Heavy geospatial dependencies are imported lazily so the package can still be
installed in lightweight environments for style/HTML work.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import numpy as np

from .bounds import Bounds


def require_rasterio():
    try:
        import rasterio
        from rasterio.transform import from_bounds
        from rasterio.warp import Resampling, reproject, transform_bounds
    except ImportError as exc:
        raise ImportError(
            "Raster operations need the 'geo' extra. Install with: "
            "pip install 'piece-of-cake-terrain[geo]'"
        ) from exc
    return rasterio, from_bounds, reproject, transform_bounds, Resampling


def require_geopandas():
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise ImportError(
            "Vector operations need the 'geo' extra. Install with: "
            "pip install 'piece-of-cake-terrain[geo]'"
        ) from exc
    return gpd


def read_raster_grid(
    path: str | Path,
    *,
    bounds: Bounds | None = None,
    width: int = 350,
    height: int | None = None,
    band: int = 1,
    dst_crs: str = "EPSG:4326",
    resampling: str = "bilinear",
) -> tuple[np.ndarray, Bounds]:
    """Read a raster into a WGS84 grid suitable for Plotly surfaces."""

    rasterio, from_bounds, reproject, transform_bounds, Resampling = require_rasterio()
    source_path = _rasterio_path(path)
    height = height or width
    resampling_enum = getattr(Resampling, resampling)

    with rasterio.open(source_path) as src:
        if bounds is None:
            min_lon, min_lat, max_lon, max_lat = transform_bounds(
                src.crs, dst_crs, *src.bounds, densify_pts=21
            )
            bounds = Bounds(min_lon, min_lat, max_lon, max_lat)
        dst_transform = from_bounds(*bounds.as_tuple(), width=width, height=height)
        dst = np.full((height, width), np.nan, dtype="float32")
        reproject(
            source=rasterio.band(src, band),
            destination=dst,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=src.nodata,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            dst_nodata=np.nan,
            resampling=resampling_enum,
        )
    return dst, bounds


def read_raster_grid_mosaic(
    paths: Sequence[str | Path],
    *,
    bounds: Bounds,
    width: int = 350,
    height: int | None = None,
    band: int = 1,
    dst_crs: str = "EPSG:4326",
    resampling: str = "nearest",
) -> tuple[np.ndarray, Bounds]:
    """Read and merge raster tiles into a WGS84 grid."""

    if not paths:
        raise ValueError("At least one raster path is required")

    rasterio, from_bounds, reproject, _transform_bounds, Resampling = require_rasterio()
    from rasterio.merge import merge

    height = height or width
    resampling_enum = getattr(Resampling, resampling)
    sources = []
    try:
        for path in paths:
            sources.append(rasterio.open(_rasterio_path(path)))
        source_crs = sources[0].crs
        source_nodata = sources[0].nodata
        mosaic, mosaic_transform = merge(
            sources,
            bounds=bounds.as_tuple() if str(source_crs).upper() == dst_crs else None,
            indexes=band,
        )
        dst_transform = from_bounds(*bounds.as_tuple(), width=width, height=height)
        dst = np.full((height, width), np.nan, dtype="float32")
        reproject(
            source=mosaic[0],
            destination=dst,
            src_transform=mosaic_transform,
            src_crs=source_crs,
            src_nodata=source_nodata,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            dst_nodata=np.nan,
            resampling=resampling_enum,
        )
    finally:
        for src in sources:
            src.close()
    return dst, bounds


def read_vector(path: str | Path, *, bounds: Bounds | None = None, layer: str | None = None):
    """Read a vector layer as WGS84 GeoDataFrame, optionally filtered by bbox."""

    gpd = require_geopandas()
    kwargs: dict[str, Any] = {}
    if layer:
        kwargs["layer"] = layer
    if bounds:
        kwargs["bbox"] = bounds.as_tuple()
    gdf = gpd.read_file(path, **kwargs)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326", allow_override=True)
    else:
        gdf = gdf.to_crs("EPSG:4326")
    if bounds:
        bbox = gpd.GeoSeries.from_wkt(
            [
                (
                    f"POLYGON(({bounds.min_lon} {bounds.min_lat}, "
                    f"{bounds.max_lon} {bounds.min_lat}, "
                    f"{bounds.max_lon} {bounds.max_lat}, "
                    f"{bounds.min_lon} {bounds.max_lat}, "
                    f"{bounds.min_lon} {bounds.min_lat}))"
                )
            ],
            crs="EPSG:4326",
        ).iloc[0]
        gdf = gdf[gdf.geometry.intersects(bbox)]
    return gdf


def _rasterio_path(path: str | Path) -> str | Path:
    value = str(path)
    if value.startswith(("http://", "https://", "s3://", "/vsicurl/")):
        return value
    return Path(path)
