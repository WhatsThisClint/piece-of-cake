# DEM Providers And Source Configs

Piece of Cake supports three DEM paths:

- local DEM rasters
- built-in provider sources such as OpenTopography
- custom provider objects for project-specific backends

## Local DEM Files

Use a local GeoTIFF when you already have one:

```python
scene.add_dem(path="dem.tif")
```

## Automatic DEM Download

Start from a bounding box and fetch a DEM from OpenTopography:

```python
from piece_of_cake import TerrainScene

scene = TerrainScene.from_bbox(76.1, 18.0, 76.4, 18.3)
scene.add_dem(source="opentopography", width=500)
scene.to_html("terrain.html")
```

`source="auto"` uses the configured default DEM source. If no config is passed,
it falls back to OpenTopography.

```python
scene.add_dem(source="auto")
```

OpenTopography API keys can be provided with the `OPENTOPOGRAPHY_API_KEY`
environment variable.

In JupyterLab or Colab, use the built-in hidden prompt:

```python
from piece_of_cake import setup_opentopography_key

setup_opentopography_key()
```

The helper checks whether `OPENTOPOGRAPHY_API_KEY` is already set. If it is not
set, it shows the MyOpenTopo dashboard link and the official OpenTopography API
key instructions before prompting with hidden input. Sign in or create an
OpenTopography account, click **Get an API Key**, then click **Request API
key**. The helper stores the key only in the current Python session. It does not
write the key to disk or return the key.

## YAML Accounts And Sources

For IHEWAcollect-style workflows, keep credentials and source choices in a YAML
file:

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

  office_dem:
    provider: local
    path: D:/gis/dem/office_dem.tif

  server_dem:
    provider: url
    url: https://example.org/dem.tif
    cache_dir: .piece-of-cake/cache
```

Then use it:

```python
scene = TerrainScene.from_bbox(76.1, 18.0, 76.4, 18.3)
scene.add_dem(source="auto", config="sources.yml")
```

Or choose a named source explicitly:

```python
scene.add_dem(source="office_dem", config="sources.yml")
```

For YAML files, install the provider extra:

```bash
pip install "piece-of-cake-terrain[geo,providers]"
```

JSON configs work without the YAML parser.

## OpenTopography Options

Common source fields:

- `dem_type`: OpenTopography DEM type such as `SRTMGL1`, `NASADEM`, `COP30`, or `COP90`.
- `api_key` or `api_key_env`: direct key or environment variable name.
- `cache_dir`: where downloaded GeoTIFFs are cached.
- `api_url`: optional override for the OpenTopography API URL.
- `timeout`: download timeout in seconds.
- `params`: extra API query parameters.

OpenTopography clips the DEM to the requested WGS84 bounding box. Piece of Cake
then reads the GeoTIFF into the requested model grid size.

## Custom Provider Objects

You can still provide your own class when a project needs special auth,
preprocessing, or server behavior:

```python
class MyDemProvider:
    def fetch_dem(self, bounds, *, width, height):
        # Download or generate DEM values here.
        # Return (numpy_array, bounds).
        return dem, bounds

scene.add_dem(provider=MyDemProvider())
```

## Why A Provider System?

- DEM licenses vary.
- Resolution varies by country and provider.
- Some sources need API keys.
- Some workflows use internal Drive or institutional data.

The provider interface lets a project connect to SRTM, Copernicus, institutional
DEMs, cached local rasters, or private servers without changing the scene engine.

## ESA WorldCover Land Cover

After adding a DEM, fetch and drape ESA WorldCover land-cover classes for the
same scene extent:

```python
scene.add_worldcover(opacity=0.55)
scene.show()
```

By default, `year="latest"` resolves to ESA WorldCover 2021 v200. The provider
reads the public AWS Cloud-Optimized GeoTIFF tiles for the current bounds and
clips/resamples them to the terrain grid. It uses the built-in
`esa_worldcover` categorical style.

```python
scene.add_worldcover(year="2021", opacity=0.45)
```

The HTML viewer includes layer opacity controls and a class-name legend, so
users can adjust and interpret the WorldCover drape without rerunning Python.
WorldCover classes are rendered as solid class masks to reduce interpolated
class-boundary halos in 3D.
