from piece_of_cake import TerrainScene


def test_scene_exports_clickable_html():
    scene = TerrainScene.from_bbox(76.0, 18.0, 76.1, 18.1)
    scene.add_dem_array([[10, 20], [15, 30]], bounds=(76.0, 18.0, 76.1, 18.1))

    html = scene.to_html()

    assert "piece-of-cake-map" in html
    assert "plotly_click" in html
    assert "Captured Points" in html
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
