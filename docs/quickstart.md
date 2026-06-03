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
