# Piece of Cake

[PyPI package](https://pypi.org/project/piece-of-cake-terrain/) |
[GitHub release](https://github.com/WhatsThisClint/piece-of-cake/releases/tag/v0.1.6)

Piece of Cake builds interactive 3D terrain scenes from DEMs, rasters, vectors, and configurable geospatial styles.

It is deliberately focused on the 3D model. Give it a DEM and optional layers, then export a clickable HTML file or display it in a Jupyter/Colab notebook.

## What It Does

- Builds Plotly-based 3D terrain from a DEM.
- Drapes custom raster layers on the terrain.
- Draws vector overlays from GeoPackages, shapefiles, GeoJSON, or other GeoPandas-readable formats.
- Lets users toggle click-capture for latitude, longitude, and elevation.
- Lets users change vertical exaggeration inside the HTML viewer.
- Fetches and drapes ESA WorldCover land-cover classes for the selected extent.
- Exports standalone HTML.
- Supports custom style profiles for unknown layers.
- Helps inspect unknown raster/vector layers before styling them.
- Can fetch DEMs from configured provider sources such as OpenTopography.

## Install

For the lightweight core:

```bash
pip install piece-of-cake-terrain
```

For geospatial raster/vector IO:

```bash
pip install "piece-of-cake-terrain[geo]"
```

For YAML source configs and provider-backed DEM download:

```bash
pip install "piece-of-cake-terrain[geo,providers]"
```

For notebook display:

```bash
pip install "piece-of-cake-terrain[geo,notebook]"
```

For place-name lookup:

```bash
pip install "piece-of-cake-terrain[geo,places]"
```

From GitHub source:

```bash
pip install "piece-of-cake-terrain[geo,places,providers] @ git+https://github.com/WhatsThisClint/piece-of-cake.git@v0.1.6"
```

For an isolated terminal command:

```bash
pipx install "piece-of-cake-terrain[geo,places]"
```

With uv:

```bash
uv tool install piece-of-cake-terrain --with rasterio --with geopandas --with pyproj --with shapely --with geopy --with PyYAML
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

Piece of Cake supports local DEM files, custom provider hooks, and configured
provider sources such as OpenTopography.

```python
scene = TerrainScene.from_bbox(76.1, 18.0, 76.4, 18.3)
scene.add_dem(path="/content/drive/MyDrive/DEM/India.tif")
```

Fetch a DEM automatically from OpenTopography:

```python
scene = TerrainScene.from_bbox(76.1, 18.0, 76.4, 18.3)
scene.add_dem(source="opentopography", width=500)
scene.to_html("terrain.html")
```

In JupyterLab or Colab, prompt for the OpenTopography key without showing it:

```python
from piece_of_cake import setup_opentopography_key

setup_opentopography_key()
```

The prompt includes a direct link to the MyOpenTopo dashboard, where users can
sign in, click **Get an API Key**, and then click **Request API key**. This
stores the key only in the current Python session.

Add ESA WorldCover land cover over the same extent:

```python
scene.add_worldcover(opacity=0.55)
scene.show()
```

`year="latest"` currently resolves to ESA WorldCover 2021 v200, the newest
WorldCover map release available from ESA.

Use an IHEWAcollect-style YAML config for accounts and named sources:

```yaml
accounts:
  opentopography:
    api_key_env: OPENTOPOGRAPHY_API_KEY

default_dem: opentopography_cop30

sources:
  opentopography_cop30:
    provider: opentopography
    dem_type: COP30
    cache_dir: .piece-of-cake/cache
```

```python
scene.add_dem(source="auto", config="sources.yml")
```

Or plug in your own provider:

```python
scene.add_dem(provider=my_dem_provider)
```

See [docs/providers.md](docs/providers.md).

## Beginner Course

A self-contained Jupyter course is available in [course/](course/). It includes
15 beginner-friendly notebooks covering DEM terrain, HTML export, bounding
boxes, DEM providers, raster drapes, custom styling, vector overlays, and a mini
diagnosis dashboard. The notebooks use synthetic local data and do not require
Drive files or public data downloads.

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

## PyPI Publishing

The package is published on PyPI as
[`piece-of-cake-terrain`](https://pypi.org/project/piece-of-cake-terrain/).
Publishing uses GitHub Actions and PyPI Trusted Publishing; see
[docs/publishing.md](docs/publishing.md).

## Citation

If you use Piece of Cake in research, reports, or public-facing tools, please cite it using the metadata in [CITATION.cff](CITATION.cff).

## License

MIT. See [LICENSE](LICENSE).
