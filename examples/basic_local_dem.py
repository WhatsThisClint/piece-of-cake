from piece_of_cake import TerrainScene


scene = TerrainScene.from_dem(
    "data/dem.tif",
    bounds=(76.1, 18.0, 76.4, 18.3),
    title="Piece of Cake demo",
)

scene.add_raster(
    "Tree Canopy",
    "data/tree_canopy.tif",
    style={
        "type": "continuous",
        "label": "Tree canopy (%)",
        "cmap": "Greens",
        "opacity": 0.65,
    },
)

scene.to_html("terrain.html")

