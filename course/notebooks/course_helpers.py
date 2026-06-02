"""Small deterministic data helpers for the Piece of Cake beginner course."""

from __future__ import annotations

from pathlib import Path

import numpy as np


BOUNDS = (76.1, 18.0, 76.4, 18.3)
OUTPUT_DIR = Path("course_outputs")


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def grid(size: int = 72) -> tuple[np.ndarray, np.ndarray]:
    x = np.linspace(-1.0, 1.0, size)
    y = np.linspace(-1.0, 1.0, size)
    return np.meshgrid(x, y)


def terrain(kind: str = "watershed", size: int = 72) -> np.ndarray:
    x, y = grid(size)
    base = 260 + 110 * (1 - y)
    hills = 80 * np.exp(-((x + 0.42) ** 2 + (y - 0.22) ** 2) * 5.5)
    hills += 55 * np.exp(-((x - 0.35) ** 2 + (y + 0.24) ** 2) * 7.0)
    valley = 90 * np.exp(-((x * 0.65) ** 2 + (y + 0.05) ** 2) * 9.0)
    if kind == "ridge":
        values = base + 155 * np.exp(-(x**2) * 14.0)
    elif kind == "valley":
        values = base + hills - valley
    elif kind == "plateau":
        values = base + 115 * (np.abs(x) < 0.42) * (np.abs(y) < 0.36)
    else:
        values = base + hills - valley
    return values.astype("float32")


def tree_canopy(size: int = 72) -> np.ndarray:
    x, y = grid(size)
    values = 20 + 60 * np.exp(-((x + 0.25) ** 2 + (y - 0.25) ** 2) * 4.5)
    values += 12 * np.sin((x + y) * 4.0)
    return np.clip(values, 0, 100).astype("float32")


def ndvi(size: int = 72) -> np.ndarray:
    canopy = tree_canopy(size) / 100
    values = 0.12 + 0.72 * canopy
    return np.clip(values, -1, 1).astype("float32")


def slope_risk(dem: np.ndarray) -> np.ndarray:
    gy, gx = np.gradient(dem.astype("float32"))
    slope = np.sqrt(gx**2 + gy**2)
    q1, q2 = np.quantile(slope, [0.45, 0.78])
    risk = np.where(slope > q2, 3, np.where(slope > q1, 2, 1))
    return risk.astype("int16")


def lulc(size: int = 72) -> np.ndarray:
    x, y = grid(size)
    values = np.full((size, size), 8, dtype="int16")
    values[y > 0.45] = 6
    values[(x > 0.35) & (y < -0.15)] = 10
    values[(x < -0.35) & (y < -0.3)] = 7
    values[np.sqrt((x + 0.05) ** 2 + (y + 0.05) ** 2) < 0.18] = 2
    return values


def soil_classes(size: int = 72) -> np.ndarray:
    x, y = grid(size)
    values = np.full((size, size), 1, dtype="int16")
    values[x > 0.15] = 2
    values[y < -0.25] = 3
    values[(x < -0.45) & (y > 0.25)] = 4
    return values


def write_raster(path: str | Path, values: np.ndarray, bounds=BOUNDS) -> Path:
    import rasterio
    from rasterio.transform import from_bounds

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    arr = np.asarray(values)
    transform = from_bounds(*bounds, width=arr.shape[1], height=arr.shape[0])
    with rasterio.open(
        output,
        "w",
        driver="GTiff",
        height=arr.shape[0],
        width=arr.shape[1],
        count=1,
        dtype=str(arr.dtype),
        crs="EPSG:4326",
        transform=transform,
    ) as dataset:
        dataset.write(arr, 1)
    return output


def write_villages(path: str | Path, bounds=BOUNDS) -> Path:
    import geopandas as gpd
    from shapely.geometry import Polygon

    min_lon, min_lat, max_lon, max_lat = bounds
    centers = [
        ("Apti", "high", 1_420, 0.24, 0.28),
        ("Borgaon", "medium", 980, 0.52, 0.44),
        ("Chincholi", "low", 760, 0.72, 0.32),
        ("Dharphal", "medium", 1_110, 0.38, 0.72),
        ("Ekurga", "high", 690, 0.68, 0.70),
    ]
    features = []
    width = max_lon - min_lon
    height = max_lat - min_lat
    half = min(width, height) * 0.025
    for name, risk, population, x_frac, y_frac in centers:
        lon = min_lon + width * x_frac
        lat = min_lat + height * y_frac
        geom = Polygon(
            [
                (lon - half, lat - half),
                (lon + half, lat - half),
                (lon + half, lat + half),
                (lon - half, lat + half),
                (lon - half, lat - half),
            ]
        )
        features.append(
            {
                "village_name": name,
                "risk_class": risk,
                "population": population,
                "sc_st_pct": round(18 + x_frac * 38, 1),
                "geometry": geom,
            }
        )
    gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    gdf.to_file(output, driver="GPKG", layer="villages")
    return output


def write_village_scores(path: str | Path, bounds=BOUNDS) -> Path:
    import geopandas as gpd
    from shapely.geometry import Polygon

    min_lon, min_lat, max_lon, max_lat = bounds
    records = [
        (101, 3, 1420, 31.2, 0.24, 0.28),
        (102, 2, 980, 22.8, 0.52, 0.44),
        (103, 1, 760, 18.4, 0.72, 0.32),
        (104, 2, 1110, 41.6, 0.38, 0.72),
        (105, 3, 690, 36.9, 0.68, 0.70),
    ]
    width = max_lon - min_lon
    height = max_lat - min_lat
    half = min(width, height) * 0.025
    features = []
    for village_code, risk_score, population, sc_st_pct, x_frac, y_frac in records:
        lon = min_lon + width * x_frac
        lat = min_lat + height * y_frac
        features.append(
            {
                "village_code": village_code,
                "risk_score": risk_score,
                "population": population,
                "sc_st_pct": sc_st_pct,
                "geometry": Polygon(
                    [
                        (lon - half, lat - half),
                        (lon + half, lat - half),
                        (lon + half, lat + half),
                        (lon - half, lat + half),
                        (lon - half, lat - half),
                    ]
                ),
            }
        )
    gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    gdf.to_file(output, driver="GPKG", layer="village_scores")
    return output


def export_scene(scene, name: str) -> tuple[Path, str]:
    output = ensure_output_dir() / name
    html = scene.to_html(output)
    assert "piece-of-cake-map" in html
    assert "plotly_click" in html
    assert output.exists()
    return output, html
