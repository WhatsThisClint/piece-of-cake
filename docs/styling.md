# Styling Layers

Piece of Cake uses style profiles. A style profile describes how values should be colored and labelled.

## Continuous Raster

Use this for values such as canopy percentage, NDVI, rainfall, groundwater depth, or elevation.

```python
style = {
    "type": "continuous",
    "label": "Tree canopy (%)",
    "cmap": "Greens",
    "opacity": 0.65,
}
```

## Categorical Raster

Use this for classes such as land cover, soil type, or risk zones.

```python
style = {
    "type": "categorical",
    "classes": {
        1: {"label": "Low", "color": "#2ca25f"},
        2: {"label": "Medium", "color": "#fee08b"},
        3: {"label": "High", "color": "#de2d26"},
    },
    "opacity": 0.70,
}
```

## Built-In Profiles

```python
from piece_of_cake import list_builtin_styles

list_builtin_styles()
```

Current built-ins include:

- `dem`
- `tree_canopy`
- `ndvi`
- `risk`
- `indiasat_lulc`
- `esa_worldcover`

