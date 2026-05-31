# Piece of Cake

Piece of Cake builds interactive 3D terrain scenes from DEMs, rasters, vectors, and configurable geospatial styles.

It is deliberately focused on the 3D model. Give it a DEM and optional layers, then export a clickable HTML file or display it in a Jupyter/Colab notebook.

## What It Does

- Builds Plotly-based 3D terrain from a DEM.
- Drapes custom raster layers on the terrain.
- Draws vector overlays from GeoPackages, shapefiles, GeoJSON, or other GeoPandas-readable formats.
- Lets users click the terrain to capture latitude, longitude, and elevation.
- Exports standalone HTML.
- Supports custom style profiles for unknown layers.
- Helps inspect unknown raster/vector layers before styling them.

## Install

From GitHub:

```bash
pip install "piece-of-cake[geo,places] @ git+https://github.com/WhatsThisClint/piece-of-cake.git@v0.1.0"
```

For the lightweight core:

```bash
pip install piece-of-cake
```

For geospatial raster/vector IO:

```bash
pip install "piece-of-cake[geo]"
```

For notebook display:

```bash
pip install "piece-of-cake[geo,notebook]"
```

For place-name lookup:

```bash
pip install "piece-of-cake[geo,places]"
```

For an isolated terminal command:

```bash
pipx install "git+https://github.com/WhatsThisClint/piece-of-cake.git@v0.1.0#egg=piece-of-cake[geo,places]"
```

With uv:

```bash
uv tool install git+https://github.com/WhatsThisClint/piece-of-cake.git@v0.1.0 --with rasterio --with geopandas --with pyproj --with shapely --with geopy
```

## Quick Start

```python
from piece_of_cake import TerrainScene

scene = TerrainScene.from_dem(
    "data/dem.tif",
    bounds=(76.1, 18.0, 76.4, 18.3),
    title="Dharashiv Terrain",
)

scene.add_raster(
    "Tree Canopy",
    "data/tree_canopy.tif",
    style={
        "type": "continuous",
        "label": "Tree canopy (%)",
        "cmap": "Greens",
        "opacity": 0.65,
    },
)

scene.to_html("dharashiv_terrain.html")
```

From the terminal:

```bash
piece-of-cake render --dem data/dem.tif --out dharashiv_terrain.html --title "Dharashiv Terrain"
```

You can also start from a place name when the optional `places` extra is installed:

```python
scene = TerrainScene.from_place("Dharashiv, Maharashtra, India")
scene.add_dem(path="data/dem.tif")
scene.to_html("dharashiv_terrain.html")
```

## Unknown Custom Layers

Piece of Cake does not assume what a custom layer means. Inspect it first:

```python
from piece_of_cake import inspect_raster, inspect_vector

inspect_raster("custom_tree_canopy.tif")
inspect_vector("villages.gpkg")
```

For a GeoPackage with many columns, choose the column explicitly:

```python
scene.add_vector(
    "SC/ST share",
    "villages.gpkg",
    column="sc_st_pct",
    label_column="village_name",
    hover_fields=["village_name", "population", "sc_st_pct"],
    style={
        "type": "continuous",
        "cmap": "Reds",
        "opacity": 0.55,
    },
)
```

## DEM Sources

Version `0.1.0` supports local DEM files and custom provider hooks. Automatic DEM download is intentionally provider-based because DEM licensing, resolution, and reliability vary by country and source.

```python
scene = TerrainScene.from_bbox(76.1, 18.0, 76.4, 18.3)
scene.add_dem(path="/content/drive/MyDrive/DEM/India.tif")
```

Or plug in your own provider:

```python
scene.add_dem(provider=my_dem_provider)
```

See [docs/providers.md](docs/providers.md).

## Terminal Commands

```bash
piece-of-cake --help
piece-of-cake render --dem data/dem.tif --out terrain.html
piece-of-cake inspect-raster custom_tree_canopy.tif
piece-of-cake inspect-vector villages.gpkg
```

If Windows cannot find `piece-of-cake` because Python's Scripts folder is not on PATH, use:

```bash
python -m piece_of_cake --help
```

See [docs/cli.md](docs/cli.md).

## Citation

If you use Piece of Cake in research, reports, or public-facing tools, please cite it using the metadata in [CITATION.cff](CITATION.cff).

## License

MIT. See [LICENSE](LICENSE).
