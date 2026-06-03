# Command Line

Piece of Cake installs a `piece-of-cake` command.

On Windows, if Python's Scripts folder is not on PATH, use `python -m piece_of_cake`
with the same arguments.

## Install From PyPI

```bash
pip install "piece-of-cake-terrain[geo,places,providers]"
```

## Install From GitHub Source

```bash
pip install "piece-of-cake-terrain[geo,places,providers] @ git+https://github.com/WhatsThisClint/piece-of-cake.git@main"
```

For an isolated command-line install:

```bash
pipx install "piece-of-cake-terrain[geo,places,providers]"
```

With uv:

```bash
uv tool install piece-of-cake-terrain --with rasterio --with geopandas --with pyproj --with shapely --with geopy --with PyYAML
```

## Render A Terrain

```bash
piece-of-cake render --dem data/dem.tif --out terrain.html
```

Equivalent module form:

```bash
python -m piece_of_cake render --dem data/dem.tif --out terrain.html
```

Useful options:

```bash
piece-of-cake render ^
  --dem data/dem.tif ^
  --out terrain.html ^
  --title "Dharashiv Terrain" ^
  --width 500 ^
  --vertical-exaggeration 1.5
```

Use explicit WGS84 bounds when the DEM bounds should be clipped or overridden:

```bash
piece-of-cake render ^
  --dem data/dem.tif ^
  --bounds 76.1 18.0 76.4 18.3 ^
  --out terrain.html
```

## Render From OpenTopography

Set an API key when using OpenTopography datasets that require one:

```bash
set OPENTOPOGRAPHY_API_KEY=your-key-here
```

Fetch a DEM from a bounding box:

```bash
piece-of-cake render ^
  --bounds 76.1 18.0 76.4 18.3 ^
  --dem-source opentopography ^
  --out terrain.html
```

Fetch from a place name:

```bash
piece-of-cake render ^
  --place "Dharashiv, Maharashtra, India" ^
  --dem-source opentopography ^
  --out terrain.html
```

Use a YAML source config:

```bash
piece-of-cake render ^
  --bounds 76.1 18.0 76.4 18.3 ^
  --sources-config sources.yml ^
  --out terrain.html
```

Add layers:

```bash
piece-of-cake render ^
  --dem data/dem.tif ^
  --raster "Tree canopy=data/tree_canopy.tif" ^
  --vector "Villages=data/villages.gpkg" ^
  --label-column village_name ^
  --hover-field population ^
  --out terrain.html
```

## Inspect Layers

```bash
piece-of-cake inspect-raster data/tree_canopy.tif
piece-of-cake inspect-vector data/villages.gpkg
```

Inspection prints JSON summaries of the layer shape, columns, sample values, and suggested style roles.
