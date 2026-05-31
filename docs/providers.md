# DEM Providers

Piece of Cake supports local DEM files immediately:

```python
scene.add_dem(path="dem.tif")
```

It also supports custom provider hooks:

```python
class MyDemProvider:
    def fetch_dem(self, bounds, *, width, height):
        # Download or generate DEM values here.
        # Return (numpy_array, bounds).
        return dem, bounds

scene.add_dem(provider=MyDemProvider())
```

Why not force one automatic DEM source?

- DEM licenses vary.
- Resolution varies by country and provider.
- Some sources need API keys.
- Some workflows use internal Drive or institutional data.

The provider interface lets a project connect to SRTM, Copernicus, institutional DEMs, or cached local rasters without changing the scene engine.

