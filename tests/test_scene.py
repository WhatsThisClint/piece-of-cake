from piece_of_cake import TerrainScene
from piece_of_cake.bounds import Bounds


def test_scene_exports_clickable_html():
    scene = TerrainScene.from_bbox(76.0, 18.0, 76.1, 18.1)
    scene.add_dem_array([[10, 20], [15, 30]], bounds=(76.0, 18.0, 76.1, 18.1))

    html = scene.to_html()

    assert "piece-of-cake-map" in html
    assert "plotly_click" in html
    assert "Terrain Controls" in html
    assert "Capture Off" in html
    assert "piece-of-cake-compass-arrow" in html
    assert "updateCompass" in html
    assert "Vertical Exaggeration" in html
    assert "Center Lock Off" in html
    assert "piece-of-cake-exaggeration" in html
    assert "piece-of-cake-exaggeration-increase" in html
    assert 'id="piece-of-cake-exaggeration" type="number"' in html
    assert 'id="piece-of-cake-exaggeration" type="range"' not in html
    assert "Layer Opacity" in html
    assert "Layer Legend" in html
    assert "pieceOfCakeLayerId" in html
    assert "item.indices" in html
    assert "contextmenu" in html
    assert "plotly_relayout" in html
    assert "Number.isFinite" in html


def test_add_dem_requires_input():
    scene = TerrainScene.from_bbox(76.0, 18.0, 76.1, 18.1)
    try:
        scene.add_dem()
    except ValueError as exc:
        assert "Provide path" in str(exc)
    else:
        raise AssertionError("add_dem should require an input source")


def test_add_dem_source_requires_bounds():
    scene = TerrainScene()
    try:
        scene.add_dem(source="auto")
    except ValueError as exc:
        assert "bounds are required" in str(exc)
    else:
        raise AssertionError("provider DEM download should require bounds")


def test_add_worldcover_uses_provider_and_style():
    class FakeWorldCoverProvider:
        def fetch_raster(self, bounds: Bounds, *, width: int, height: int):
            assert bounds == Bounds(76.0, 18.0, 76.1, 18.1)
            assert width == 2
            assert height == 2
            return [[10, 50], [80, 40]], bounds

    scene = TerrainScene.from_bbox(76.0, 18.0, 76.1, 18.1)
    scene.add_dem_array([[10, 20], [15, 30]], bounds=(76.0, 18.0, 76.1, 18.1))
    scene.add_worldcover(provider=FakeWorldCoverProvider(), opacity=0.55)

    assert len(scene.raster_overlays) == 1
    overlay = scene.raster_overlays[0]
    assert overlay.name == "ESA WorldCover"
    assert overlay.style.kind == "categorical"
    assert overlay.style.opacity == 0.55
    assert overlay.style.classes[50]["label"] == "Built-up"

    html = scene.to_html()

    assert "ESA WorldCover" in html
    assert "Built-up" in html
    assert "Layer Opacity" in html
    assert "Layer Legend" in html


def test_categorical_worldcover_uses_class_legend_not_numeric_colorbar():
    class FakeWorldCoverProvider:
        def fetch_raster(self, bounds: Bounds, *, width: int, height: int):
            return [[10, 50], [80, 40]], bounds

    scene = TerrainScene.from_bbox(76.0, 18.0, 76.1, 18.1)
    scene.add_dem_array([[10, 20], [15, 30]], bounds=(76.0, 18.0, 76.1, 18.1))
    scene.add_worldcover(provider=FakeWorldCoverProvider(), opacity=0.55)

    fig = scene.to_figure()
    colorbars = [trace.colorbar for trace in fig.data if getattr(trace, "showscale", False)]
    worldcover_traces = fig.data[1:]

    assert len(colorbars) == 1
    assert fig.layout.margin.r >= 100
    assert len(worldcover_traces) == 4
    assert all(trace.showscale is False for trace in worldcover_traces)
    assert all(trace.cmin == 0 for trace in worldcover_traces)
    assert all(trace.cmax == 1 for trace in worldcover_traces)
    assert all(trace.meta["pieceOfCakeLayerId"] == "raster-0" for trace in worldcover_traces)
    assert [trace.name for trace in worldcover_traces] == [
        "ESA WorldCover: Tree cover",
        "ESA WorldCover: Cropland",
        "ESA WorldCover: Built-up",
        "ESA WorldCover: Permanent water bodies",
    ]
    assert worldcover_traces[0].meta["pieceOfCakeClasses"] == [
        {"value": 10, "index": 0, "label": "Tree cover", "color": "#006400"},
        {"value": 40, "index": 3, "label": "Cropland", "color": "#f096ff"},
        {"value": 50, "index": 4, "label": "Built-up", "color": "#fa0000"},
        {"value": 80, "index": 7, "label": "Permanent water bodies", "color": "#0064c8"},
    ]
    assert all("pieceOfCakeClasses" not in trace.meta for trace in worldcover_traces[1:])
