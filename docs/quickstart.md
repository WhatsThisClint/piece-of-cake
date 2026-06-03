# Quick Start

```python
from piece_of_cake import TerrainScene

scene = TerrainScene.from_dem(
    "dem.tif",
    bounds=(76.1, 18.0, 76.4, 18.3),
    title="Terrain model",
)

scene.to_html("terrain.html")
```

Add a raster drape:

```python
scene.add_raster(
    "Cropping Intensity",
    "cropping_intensity.tif",
    style={
        "type": "continuous",
        "cmap": "YlGn",
        "opacity": 0.65,
    },
)
```

Add a vector overlay:

```python
scene.add_vector(
    "Villages",
    "villages.gpkg",
    label_column="village_name",
    hover_fields=["village_name", "population"],
    style={
        "type": "single",
        "outline": "#111827",
    },
)
```

Display in a notebook:

```python
scene.show()
```

The HTML viewer includes a controls panel for vertical exaggeration, reset/top
view, center lock, a north compass, layer opacity, categorical legends, and click-capture.
Capture is off by default so dragging the terrain does not keep saving points.

Use the terminal command:

```bash
piece-of-cake render --dem dem.tif --out terrain.html
```

Fetch a DEM from a configured provider instead of passing a DEM file:

```python
from piece_of_cake import setup_opentopography_key

setup_opentopography_key()

scene = TerrainScene.from_bbox(76.1, 18.0, 76.4, 18.3)
scene.add_dem(source="opentopography", width=500)
scene.to_html("terrain.html")
```

The hidden prompt includes a link to the MyOpenTopo dashboard. Sign in or create
an OpenTopography account, click **Get an API Key**, then click **Request API
key** and paste it into the prompt.

Add ESA WorldCover land cover for the same extent:

```python
scene.add_worldcover(opacity=0.55)
scene.show()
```

The viewer includes opacity controls for draped layers and class-name legends
for categorical drapes such as ESA WorldCover. Categorical drapes are rendered
as solid class masks to reduce blended boundaries between land-cover classes.

With a YAML source config:

```python
scene.add_dem(source="auto", config="sources.yml")
```

Start from a place name:

```bash
pip install "piece-of-cake-terrain[geo,places,providers]"
```

```python
scene = TerrainScene.from_place("Dharashiv, Maharashtra, India")
scene.add_dem(source="opentopography")
scene.to_html("terrain.html")
```
