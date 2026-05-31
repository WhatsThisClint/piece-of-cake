# Piece of Cake Documentation

Piece of Cake is a small Python package for creating clickable 3D terrain HTML scenes from geospatial layers.

The main class is `TerrainScene`.

```python
from piece_of_cake import TerrainScene
```

Use it when you want:

- a 3D DEM terrain viewer
- configurable raster drapes
- vector overlays
- click-to-capture coordinates/elevation
- standalone HTML export
- notebook display

The package intentionally separates the 3D scene engine from report generation.

## Guides

- [Quick start](quickstart.md)
- [Command line](cli.md)
- [Styling custom layers](styling.md)
- [Custom layers](custom-layers.md)
- [DEM providers](providers.md)
