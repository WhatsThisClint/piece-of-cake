from piece_of_cake.cli import _parse_layer_spec, build_parser


def test_cli_parser_supports_render_command():
    parser = build_parser()

    args = parser.parse_args(["render", "--dem", "dem.tif", "--out", "terrain.html"])

    assert args.command == "render"
    assert args.dem == "dem.tif"
    assert args.out == "terrain.html"


def test_parse_named_layer_spec():
    assert _parse_layer_spec("Tree canopy=data/tree.tif") == ("Tree canopy", "data/tree.tif")


def test_parse_path_only_layer_spec():
    assert _parse_layer_spec("data/tree_canopy.tif") == ("tree_canopy", "data/tree_canopy.tif")
