"""Piece of Cake: interactive 3D terrain scenes for geospatial layers."""

from .inspectors import inspect_raster, inspect_vector
from .providers import (
    DemProvider,
    EsaWorldCoverProvider,
    LocalRasterProvider,
    OpenTopographyProvider,
    RasterProvider,
    SourcesConfig,
    UrlRasterProvider,
    build_dem_provider,
    load_sources_config,
    setup_opentopography_key,
    worldcover_tiles,
)
from .scene import TerrainScene
from .styles import StyleProfile, auto_style, built_in_style, list_builtin_styles

__all__ = [
    "DemProvider",
    "EsaWorldCoverProvider",
    "LocalRasterProvider",
    "OpenTopographyProvider",
    "RasterProvider",
    "SourcesConfig",
    "StyleProfile",
    "TerrainScene",
    "UrlRasterProvider",
    "auto_style",
    "build_dem_provider",
    "built_in_style",
    "inspect_raster",
    "inspect_vector",
    "list_builtin_styles",
    "load_sources_config",
    "setup_opentopography_key",
    "worldcover_tiles",
]

__version__ = "0.1.6"
