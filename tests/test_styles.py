from piece_of_cake import auto_style, built_in_style, list_builtin_styles
from piece_of_cake.styles import categorical_colorscale


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


def test_categorical_colorscale_uses_hard_color_steps():
    profile = built_in_style("risk")

    colorscale, value_map = categorical_colorscale(profile)

    assert value_map == {1: 0, 2: 1, 3: 2}
    assert colorscale == [
        [0.0, "#2ca25f"],
        [1 / 3, "#2ca25f"],
        [1 / 3, "#fee08b"],
        [2 / 3, "#fee08b"],
        [2 / 3, "#de2d26"],
        [1.0, "#de2d26"],
    ]
