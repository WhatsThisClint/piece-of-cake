# Changelog

## 0.1.2 - 2026-06-03

- Added DEM source configs inspired by account/source registry workflows.
- Added built-in OpenTopography DEM download support.
- Added local and URL raster DEM providers.
- Added `source=` and `config=` support to `TerrainScene.add_dem()`.
- Added CLI provider-backed DEM rendering from bounds or place names.
- Added provider documentation, example source config, and tests.

## 0.1.1 - 2026-05-31

- Renamed the PyPI distribution to `piece-of-cake-terrain`.
- Kept the Python import package as `piece_of_cake`.
- Kept the command-line executable as `piece-of-cake`.

## 0.1.0 - 2026-05-31

- Initial package scaffold.
- Added `TerrainScene` for DEM-based 3D terrain scenes.
- Added raster drapes, vector overlays, HTML export, and notebook display.
- Added click-to-capture latitude, longitude, and elevation in exported HTML.
- Added layer inspection helpers for unknown rasters and vectors.
- Added built-in style profiles and custom style dictionaries.
- Added command-line `render`, `inspect-raster`, and `inspect-vector` commands.
- Added MIT license and citation metadata.
