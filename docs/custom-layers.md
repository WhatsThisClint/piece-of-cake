# Custom Layers

Custom layers should be inspected before styling.

## Raster Inspection

```python
from piece_of_cake import inspect_raster

profile = inspect_raster("tree_canopy.tif")
profile
```

The inspector reports:

- raster size
- CRS
- value range
- sample unique values
- suggested style type

If the raster has many numeric values, use a continuous style. If it has a small number of values, use a categorical style.

## Vector Inspection

```python
from piece_of_cake import inspect_vector

profile = inspect_vector("villages.gpkg")
profile["suggested_columns"]
```

For GeoPackages with many columns, choose explicitly:

```python
scene.add_vector(
    "Groundwater status",
    "villages.gpkg",
    column="gw_status",
    label_column="village_name",
    hover_fields=["village_name", "gw_status"],
    style={"type": "categorical"},
)
```

The package can suggest columns, but it should not silently decide the meaning of local data.

