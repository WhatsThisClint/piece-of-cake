from piece_of_cake.cli import _parse_layer_spec, build_parser


def test_cli_parser_supports_render_command():
    parser = build_parser()

    args = parser.parse_args(["render", "--dem", "dem.tif", "--out", "terrain.html"])

    assert args.command == "render"
    assert args.dem == "dem.tif"
    assert args.out == "terrain.html"


def test_cli_parser_supports_provider_dem_download():
    parser = build_parser()

    args = parser.parse_args(
        [
            "render",
            "--bounds",
            "76",
            "18",
            "76.1",
            "18.1",
            "--dem-source",
            "opentopography",
            "--sources-config",
            "sources.yml",
            "--out",
            "terrain.html",
        ]
    )

    assert args.command == "render"
    assert args.dem is None
    assert args.dem_source == "opentopography"
    assert args.sources_config == "sources.yml"


def test_parse_named_layer_spec():
    assert _parse_layer_spec("Tree canopy=data/tree.tif") == ("Tree canopy", "data/tree.tif")


def test_parse_path_only_layer_spec():
    assert _parse_layer_spec("data/tree_canopy.tif") == ("tree_canopy", "data/tree_canopy.tif")
