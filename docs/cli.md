# Command Line

Piece of Cake installs a `piece-of-cake` command.

On Windows, if Python's Scripts folder is not on PATH, use `python -m piece_of_cake`
with the same arguments.

## Install From GitHub

```bash
pip install "piece-of-cake-terrain[geo,places] @ git+https://github.com/WhatsThisClint/piece-of-cake.git@v0.1.1"
```

For an isolated command-line install:

```bash
pipx install "git+https://github.com/WhatsThisClint/piece-of-cake.git@v0.1.1#egg=piece-of-cake-terrain[geo,places]"
```

With uv:

```bash
uv tool install git+https://github.com/WhatsThisClint/piece-of-cake.git@v0.1.1 --with rasterio --with geopandas --with pyproj --with shapely --with geopy
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
