"""Command-line entry point for Piece of Cake."""

from __future__ import annotations

import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Sequence

from .bounds import Bounds
from .inspectors import inspect_raster, inspect_vector
from .scene import TerrainScene


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="piece-of-cake",
        description="Build clickable 3D terrain HTML scenes from DEMs and map layers.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {_package_version()}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    render = subparsers.add_parser("render", help="Render a DEM as an interactive 3D HTML file.")
    render.add_argument("--dem", help="Path to the DEM raster.")
    render.add_argument(
        "--dem-source",
        help="Named DEM source from --sources-config, or a built-in source such as opentopography.",
    )
    render.add_argument("--sources-config", help="YAML/JSON accounts and sources config file.")
    render.add_argument("--place", help="Place name to geocode before fetching a DEM.")
    render.add_argument(
        "--buffer-degrees",
        type=float,
        default=0.05,
        help="Place-name buffer in WGS84 degrees. Used with --place.",
    )
    render.add_argument("--out", required=True, help="Output HTML path.")
    render.add_argument("--title", default="Piece of Cake Terrain", help="Scene title.")
    render.add_argument("--width", type=int, default=350, help="Output terrain grid width.")
    render.add_argument("--height", type=int, help="Output terrain grid height. Defaults to width.")
    render.add_argument(
        "--bounds",
        nargs=4,
        type=float,
        metavar=("MIN_LON", "MIN_LAT", "MAX_LON", "MAX_LAT"),
        help="Optional WGS84 bounds. If omitted, bounds are read from the DEM.",
    )
    render.add_argument(
        "--vertical-exaggeration",
        type=float,
        default=1.0,
        help="Vertical exaggeration multiplier.",
    )
    render.add_argument(
        "--include-plotlyjs",
        default="cdn",
        choices=("cdn", "inline", "directory"),
        help="How Plotly JavaScript should be included in the output HTML.",
    )
    render.add_argument(
        "--raster",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Raster layer to drape. Repeat for multiple layers.",
    )
    render.add_argument(
        "--vector",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Vector layer to overlay. Repeat for multiple layers.",
    )
    render.add_argument("--vector-layer", help="GeoPackage/vector layer name for vector overlays.")
    render.add_argument("--vector-column", help="Attribute column to color vector overlays by.")
    render.add_argument("--label-column", help="Attribute column to show as the vector label.")
    render.add_argument(
        "--hover-field",
        action="append",
        default=[],
        help="Attribute column to show in vector hover text. Repeat for multiple fields.",
    )
    render.set_defaults(func=_render)

    raster = subparsers.add_parser("inspect-raster", help="Inspect a raster before styling it.")
    raster.add_argument("path", help="Raster path.")
    raster.add_argument("--band", type=int, default=1, help="Raster band to inspect.")
    raster.add_argument("--max-unique", type=int, default=32, help="Maximum sample values to print.")
    raster.set_defaults(func=_inspect_raster)

    vector = subparsers.add_parser("inspect-vector", help="Inspect vector columns before styling.")
    vector.add_argument("path", help="Vector path.")
    vector.add_argument("--layer", help="Optional vector layer name.")
    vector.add_argument("--max-unique", type=int, default=24, help="Maximum sample values per column.")
    vector.set_defaults(func=_inspect_vector)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print(f"piece-of-cake: error: {exc}", file=sys.stderr)
        return 1


def _render(args: argparse.Namespace) -> int:
    bounds = Bounds.from_tuple(tuple(args.bounds)) if args.bounds else None
    if args.place and bounds:
        raise ValueError("Use either --place or --bounds, not both")

    if args.place:
        scene = TerrainScene.from_place(
            args.place,
            buffer_degrees=args.buffer_degrees,
            title=args.title,
        )
    elif bounds:
        scene = TerrainScene.from_bbox(*bounds.as_tuple(), title=args.title)
    else:
        scene = TerrainScene(title=args.title)

    if args.dem:
        scene.add_dem(path=args.dem, width=args.width, height=args.height)
    else:
        if scene.bounds is None:
            raise ValueError("Provide --dem, or provide --bounds/--place for provider DEM download")
        scene.add_dem(
            source=args.dem_source or "auto",
            config=args.sources_config,
            width=args.width,
            height=args.height,
        )

    scene.vertical_exaggeration = args.vertical_exaggeration

    for spec in args.raster:
        name, path = _parse_layer_spec(spec)
        scene.add_raster(name, path)

    for spec in args.vector:
        name, path = _parse_layer_spec(spec)
        scene.add_vector(
            name,
            path,
            layer=args.vector_layer,
            column=args.vector_column,
            label_column=args.label_column,
            hover_fields=args.hover_field,
        )

    output = Path(args.out)
    scene.to_html(output, include_plotlyjs=args.include_plotlyjs)
    print(f"Wrote {output.resolve()}")
    return 0


def _inspect_raster(args: argparse.Namespace) -> int:
    _print_json(inspect_raster(args.path, band=args.band, max_unique=args.max_unique))
    return 0


def _inspect_vector(args: argparse.Namespace) -> int:
    _print_json(inspect_vector(args.path, layer=args.layer, max_unique=args.max_unique))
    return 0


def _parse_layer_spec(spec: str) -> tuple[str, str]:
    if "=" in spec:
        name, path = spec.split("=", 1)
        name = name.strip()
        path = path.strip()
        if not name or not path:
            raise ValueError(f"Layer specs must look like NAME=PATH, got {spec!r}")
        return name, path

    path = spec.strip()
    if not path:
        raise ValueError("Layer path cannot be empty")
    return Path(path).stem, path


def _print_json(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, default=str))


def _package_version() -> str:
    try:
        return version("piece-of-cake-terrain")
    except PackageNotFoundError:
        return "0.1.4"


if __name__ == "__main__":
    raise SystemExit(main())
