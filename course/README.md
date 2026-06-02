# Piece of Cake Beginner Course

This course teaches `piece-of-cake-terrain` through 15 beginner-friendly Jupyter
notebooks. Every module uses deterministic synthetic data, so nothing depends on
Drive files, public APIs, or external downloads.

## Setup

Install the package with the geospatial and notebook extras:

```bash
pip install "piece-of-cake-terrain[geo,notebook,places]"
```

From a local clone of this repository, install the same capabilities in editable
mode:

```bash
pip install -e ".[geo,notebook]"
```

Then open the notebooks in `course/notebooks/`. Exported HTML, GeoTIFF, and
GeoPackage files are written to `course_outputs/`, which is ignored by Git.

## Colab Note

If you open an individual notebook in Google Colab, `course_helpers.py` may not
be present beside it. Each notebook now checks for that file and downloads it
from this GitHub repository when needed. You only need to install the package:

```bash
pip install "piece-of-cake-terrain[geo,notebook]"
```

## Learning Path

1. [First 3D Terrain](notebooks/01_first_3d_terrain.ipynb)
2. [Reading Terrain Shape](notebooks/02_reading_terrain_shape.ipynb)
3. [Exporting HTML](notebooks/03_exporting_html.ipynb)
4. [Bounding Boxes](notebooks/04_bounding_boxes.ipynb)
5. [Custom DEM Provider](notebooks/05_custom_dem_provider.ipynb)
6. [Watershed Relief Story](notebooks/06_watershed_relief_story.ipynb)
7. [Slope Risk Proxy](notebooks/07_slope_risk_proxy.ipynb)
8. [Tree Canopy Layer](notebooks/08_tree_canopy_layer.ipynb)
9. [NDVI Layer](notebooks/09_ndvi_layer.ipynb)
10. [Land Use Classes](notebooks/10_land_use_classes.ipynb)
11. [Custom Theming](notebooks/11_custom_theming.ipynb)
12. [Inspect Unknown Raster](notebooks/12_inspect_unknown_raster.ipynb)
13. [Village Overlay](notebooks/13_village_point_overlay.ipynb)
14. [Choosing Vector Columns](notebooks/14_choosing_vector_columns.ipynb)
15. [Mini Diagnosis Dashboard Export](notebooks/15_mini_diagnosis_dashboard_export.ipynb)

## What Learners Build

- Clickable 3D terrain HTML exports.
- Synthetic DEMs for ridges, valleys, plateaus, and watershed-like relief.
- Raster drapes for risk, tree canopy, NDVI, land use, and custom classes.
- Vector overlays with labels and hover fields.
- A combined mini diagnosis terrain export.

## Notes For Teachers

- The notebooks are intentionally small and repetitive so beginners can see the
  same workflow in different contexts.
- The data helpers live in `course/notebooks/course_helpers.py`.
- The course test executes notebook code cells headlessly and checks that the
  generated HTML contains the Plotly terrain div and click handler.
