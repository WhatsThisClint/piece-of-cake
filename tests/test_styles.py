from piece_of_cake import auto_style, built_in_style, list_builtin_styles


def test_builtin_styles_include_known_lulc_profiles():
    names = list_builtin_styles()

    assert "indiasat_lulc" in names
    assert "esa_worldcover" in names


def test_auto_style_detects_small_integer_classes():
    profile = auto_style([1, 1, 2, 3])

    assert profile.kind == "categorical"
    assert 1 in profile.classes


def test_builtin_style_returns_copy():
    profile = built_in_style("tree_canopy")
    profile.cmap = "Viridis"

    assert built_in_style("tree_canopy").cmap == "Greens"

