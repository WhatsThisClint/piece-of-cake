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
    assert "Vertical Exaggeration" in html
    assert "Center Lock Off" in html
    assert "piece-of-cake-exaggeration" in html
    assert "Layer Opacity" in html
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
    assert "Layer Opacity" in html
