"""Piece of Cake: interactive 3D terrain scenes for geospatial layers."""

from .inspectors import inspect_raster, inspect_vector
from .scene import TerrainScene
from .styles import StyleProfile, auto_style, built_in_style, list_builtin_styles

__all__ = [
    "StyleProfile",
    "TerrainScene",
    "auto_style",
    "built_in_style",
    "inspect_raster",
    "inspect_vector",
    "list_builtin_styles",
]

__version__ = "0.1.1"
