"""High-level scene builder for interactive 3D terrain HTML."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

import numpy as np
import plotly.graph_objects as go

from .bounds import Bounds
from .io import read_raster_grid, read_vector
from .styles import StyleProfile, auto_style, categorical_colorscale


class DemProvider(Protocol):
    """Protocol for custom DEM download/provider integrations."""

    def fetch_dem(self, bounds: Bounds, *, width: int, height: int) -> tuple[np.ndarray, Bounds]:
        """Return ``(dem_array, bounds)`` for the requested WGS84 bounds."""


@dataclass
class RasterOverlay:
    name: str
    values: np.ndarray
    style: StyleProfile


@dataclass
class VectorOverlay:
    name: str
    features: Any
    style: StyleProfile
    column: str | None = None
    label_column: str | None = None
    hover_fields: list[str] = field(default_factory=list)


@dataclass
class TerrainScene:
    """An interactive terrain scene.

    Use ``from_bbox`` or ``from_dem`` to start, add rasters/vectors, then export
    HTML or display in a notebook.
    """

    title: str = "Piece of Cake Terrain"
    bounds: Bounds | None = None
    dem: np.ndarray | None = None
    vertical_exaggeration: float = 1.0
    raster_overlays: list[RasterOverlay] = field(default_factory=list)
    vector_overlays: list[VectorOverlay] = field(default_factory=list)

    @classmethod
    def from_bbox(
        cls,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float,
        *,
        title: str = "Piece of Cake Terrain",
    ) -> "TerrainScene":
        return cls(title=title, bounds=Bounds(min_lon, min_lat, max_lon, max_lat))

    @classmethod
    def from_place(
        cls,
        place: str,
        *,
        buffer_degrees: float = 0.05,
        title: str | None = None,
        geocoder_user_agent: str = "piece-of-cake",
    ) -> "TerrainScene":
        """Create bounds from a place name using optional ``geopy``.

        This resolves a place but does not download a DEM by itself. Call
        ``add_dem(path=...)`` or ``add_dem(provider=...)`` afterwards.
        """

        try:
            from geopy.geocoders import Nominatim
        except ImportError as exc:
            raise ImportError(
                "Place-name lookup needs geopy. Install with: pip install geopy"
            ) from exc

        geocoder = Nominatim(user_agent=geocoder_user_agent)
        location = geocoder.geocode(place)
        if location is None:
            raise ValueError(f"Could not geocode place: {place!r}")
        bounds = Bounds.from_center(location.longitude, location.latitude, buffer_degrees)
        return cls(title=title or f"Piece of Cake Terrain - {place}", bounds=bounds)

    @classmethod
    def from_dem(
        cls,
        path: str | Path,
        *,
        bounds: Bounds | tuple[float, float, float, float] | None = None,
        width: int = 350,
        height: int | None = None,
        title: str = "Piece of Cake Terrain",
    ) -> "TerrainScene":
        scene = cls(title=title, bounds=_coerce_bounds(bounds))
        scene.add_dem(path=path, width=width, height=height)
        return scene

    def add_dem(
        self,
        path: str | Path | None = None,
        *,
        source: str | None = None,
        provider: DemProvider | None = None,
        width: int = 350,
        height: int | None = None,
    ) -> "TerrainScene":
        """Load or fetch a DEM for the scene.

        ``source=\"auto\"`` is intentionally reserved for user-provided provider
        integrations. Public DEM licensing, resolution, and availability vary by
        region, so automatic download should be explicit.
        """

        height = height or width
        if path:
            dem, bounds = read_raster_grid(path, bounds=self.bounds, width=width, height=height)
        elif provider:
            if self.bounds is None:
                raise ValueError("bounds are required when fetching a DEM from a provider")
            dem, bounds = provider.fetch_dem(self.bounds, width=width, height=height)
        elif source == "auto":
            raise NotImplementedError(
                "Automatic DEM download is provider-based. Pass provider=YourDemProvider() "
                "or use add_dem(path='local_dem.tif')."
            )
        else:
            raise ValueError("Provide path=..., provider=..., or source='auto'")

        self.dem = np.asarray(dem, dtype="float32")
        self.bounds = bounds
        return self

    def add_dem_array(
        self,
        values: np.ndarray,
        *,
        bounds: Bounds | tuple[float, float, float, float],
    ) -> "TerrainScene":
        self.dem = np.asarray(values, dtype="float32")
        self.bounds = _coerce_bounds(bounds)
        return self

    def add_raster(
        self,
        name: str,
        path: str | Path,
        *,
        style: StyleProfile | dict[str, Any] | str | None = None,
        resampling: str = "nearest",
    ) -> "TerrainScene":
        self._require_dem()
        height, width = self.dem.shape
        values, _ = read_raster_grid(
            path,
            bounds=self.bounds,
            width=width,
            height=height,
            resampling=resampling,
        )
        profile = StyleProfile.from_value(style) if style else auto_style(values)
        self.raster_overlays.append(RasterOverlay(name=name, values=values, style=profile))
        return self

    def add_vector(
        self,
        name: str,
        path: str | Path,
        *,
        layer: str | None = None,
        column: str | None = None,
        label_column: str | None = None,
        hover_fields: list[str] | None = None,
        style: StyleProfile | dict[str, Any] | str | None = None,
    ) -> "TerrainScene":
        self._require_dem()
        gdf = read_vector(path, bounds=self.bounds, layer=layer)
        profile = StyleProfile.from_value(style) if style else StyleProfile(kind="single")
        self.vector_overlays.append(
            VectorOverlay(
                name=name,
                features=gdf,
                style=profile,
                column=column,
                label_column=label_column,
                hover_fields=hover_fields or [],
            )
        )
        return self

    def to_figure(self) -> go.Figure:
        self._require_dem()
        assert self.bounds is not None
        z = _scaled_dem(self.dem, self.vertical_exaggeration)
        height, width = z.shape
        customdata = _customdata_grid(self.dem, self.bounds)

        traces: list[go.BaseTraceType] = [
            go.Surface(
                z=z,
                surfacecolor=self.dem,
                colorscale="Earth",
                customdata=customdata,
                name="DEM",
                showscale=True,
                colorbar={"title": "Elevation"},
                hovertemplate=(
                    "Lat %{customdata[0]:.5f}<br>"
                    "Lon %{customdata[1]:.5f}<br>"
                    "Elev %{customdata[2]:.1f}<extra>DEM</extra>"
                ),
            )
        ]
        relief = _safe_relief(z)

        for overlay in self.raster_overlays:
            traces.append(_raster_surface_trace(overlay, z, relief, customdata))

        for overlay in self.vector_overlays:
            traces.extend(_vector_traces(overlay, z, self.bounds))

        fig = go.Figure(data=traces)
        fig.update_layout(
            title=self.title,
            margin={"l": 0, "r": 0, "t": 45, "b": 0},
            scene={
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "zaxis": {"title": "Elevation"},
                "aspectmode": "manual",
                "aspectratio": {"x": 1, "y": 1, "z": 0.25},
                "dragmode": "turntable",
            },
            legend={"orientation": "h", "y": 0.02, "x": 0.02},
        )
        return fig

    def to_html(self, path: str | Path | None = None, *, include_plotlyjs: str = "cdn") -> str:
        fig = self.to_figure()
        html = fig.to_html(
            include_plotlyjs=include_plotlyjs,
            full_html=True,
            div_id="piece-of-cake-map",
            config={"responsive": True, "scrollZoom": True},
        )
        html = inject_click_tools(html)
        if path:
            Path(path).write_text(html, encoding="utf-8")
        return html

    def show(self):
        """Display the scene in a Jupyter notebook."""

        try:
            from IPython.display import HTML, display
        except ImportError as exc:
            raise ImportError("Notebook display needs IPython. Install the 'notebook' extra.") from exc
        display(HTML(self.to_html(include_plotlyjs="cdn")))

    def _require_dem(self) -> None:
        if self.dem is None or self.bounds is None:
            raise ValueError("Add a DEM first with add_dem(), add_dem_array(), or from_dem().")


def inject_click_tools(html: str) -> str:
    """Add a small click-to-capture sidebar to a Plotly HTML document."""

    sidebar = r"""
<style>
  #piece-of-cake-panel {
    position: fixed;
    top: 16px;
    right: 16px;
    width: 300px;
    max-height: calc(100vh - 32px);
    overflow: auto;
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid #d1d5db;
    border-radius: 8px;
    box-shadow: 0 12px 32px rgba(17, 24, 39, 0.16);
    color: #111827;
    font: 13px/1.4 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    padding: 12px;
    z-index: 9999;
  }
  #piece-of-cake-panel h2 {
    font-size: 14px;
    margin: 0 0 8px;
  }
  #piece-of-cake-points {
    display: grid;
    gap: 8px;
    margin: 10px 0;
  }
  .piece-of-cake-point {
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 8px;
    background: #f9fafb;
  }
  #piece-of-cake-panel button {
    border: 1px solid #9ca3af;
    background: #ffffff;
    color: #111827;
    border-radius: 6px;
    padding: 6px 9px;
    cursor: pointer;
    margin-right: 6px;
  }
  #piece-of-cake-panel button.primary {
    background: #14532d;
    border-color: #14532d;
    color: white;
  }
</style>
<aside id="piece-of-cake-panel">
  <h2>Captured Points</h2>
  <div>Click the terrain to save latitude, longitude, and elevation.</div>
  <div id="piece-of-cake-points"></div>
  <button class="primary" id="piece-of-cake-copy">Copy CSV</button>
  <button id="piece-of-cake-clear">Clear</button>
</aside>
<script>
(function() {
  const points = [];

  function fmt(value, digits) {
    return Number.isFinite(value) ? value.toFixed(digits) : "";
  }

  function render() {
    const list = document.getElementById("piece-of-cake-points");
    if (!list) return;
    if (points.length === 0) {
      list.innerHTML = '<div style="color:#6b7280">No points captured yet.</div>';
      return;
    }
    list.innerHTML = points.map(function(p, idx) {
      return '<div class="piece-of-cake-point"><strong>Point ' + (idx + 1) + '</strong><br>' +
        'Lat: ' + fmt(p.lat, 6) + '<br>' +
        'Lon: ' + fmt(p.lon, 6) + '<br>' +
        'Elev: ' + fmt(p.elev, 2) + '</div>';
    }).join("");
  }

  function copyCsv() {
    const csv = "index,lat,lon,elevation\n" + points.map(function(p, idx) {
      return [idx + 1, p.lat, p.lon, p.elev].join(",");
    }).join("\n");
    navigator.clipboard.writeText(csv);
  }

  function attach() {
    const plot = document.getElementById("piece-of-cake-map");
    if (!plot || !plot.on) {
      window.setTimeout(attach, 100);
      return;
    }
    plot.on("plotly_click", function(event) {
      if (!event.points || event.points.length === 0) return;
      const point = event.points[0];
      const data = point.customdata || [];
      const lat = Number(data[0]);
      const lon = Number(data[1]);
      const elev = Number.isFinite(Number(data[2])) ? Number(data[2]) : Number(point.z || 0);
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
      points.push({lat: lat, lon: lon, elev: elev});
      render();
    });
  }

  document.getElementById("piece-of-cake-copy").addEventListener("click", copyCsv);
  document.getElementById("piece-of-cake-clear").addEventListener("click", function() {
    points.length = 0;
    render();
  });
  render();
  attach();
})();
</script>
"""
    return html.replace("</body>", sidebar + "\n</body>")


def _coerce_bounds(value: Bounds | tuple[float, float, float, float] | None) -> Bounds | None:
    if value is None:
        return None
    if isinstance(value, Bounds):
        return value
    return Bounds.from_tuple(value)


def _scaled_dem(dem: np.ndarray, vertical_exaggeration: float) -> np.ndarray:
    clean = np.asarray(dem, dtype="float32")
    minimum = np.nanmin(clean)
    return np.where(np.isfinite(clean), (clean - minimum) * vertical_exaggeration, np.nan)


def _safe_relief(z: np.ndarray) -> float:
    relief = float(np.nanmax(z) - np.nanmin(z))
    return relief if np.isfinite(relief) and relief > 0 else 1.0


def _customdata_grid(dem: np.ndarray, bounds: Bounds) -> np.ndarray:
    height, width = dem.shape
    lons = np.linspace(bounds.min_lon, bounds.max_lon, width)
    lats = np.linspace(bounds.max_lat, bounds.min_lat, height)
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    return np.dstack([lat_grid, lon_grid, dem])


def _raster_surface_trace(
    overlay: RasterOverlay,
    base_z: np.ndarray,
    relief: float,
    customdata: np.ndarray,
) -> go.Surface:
    style = overlay.style
    z = base_z + relief * 0.006
    values = overlay.values
    if style.kind == "categorical":
        colorscale, value_map = categorical_colorscale(style)
        surfacecolor = np.full(values.shape, np.nan, dtype="float32")
        for raw_value, mapped_value in value_map.items():
            surfacecolor[values == raw_value] = mapped_value
        cmin, cmax = 0, max(len(value_map) - 1, 1)
    else:
        surfacecolor = values
        colorscale = style.cmap
        finite = surfacecolor[np.isfinite(surfacecolor)]
        cmin = float(finite.min()) if finite.size else None
        cmax = float(finite.max()) if finite.size else None

    return go.Surface(
        z=z,
        surfacecolor=surfacecolor,
        colorscale=colorscale,
        cmin=cmin,
        cmax=cmax,
        opacity=style.opacity,
        customdata=customdata,
        name=overlay.name,
        showscale=style.legend,
        colorbar={"title": style.label or overlay.name},
        hovertemplate=(
            f"{overlay.name}<br>"
            "Lat %{customdata[0]:.5f}<br>"
            "Lon %{customdata[1]:.5f}<br>"
            "Elev %{customdata[2]:.1f}<extra></extra>"
        ),
    )


def _vector_traces(overlay: VectorOverlay, z: np.ndarray, bounds: Bounds) -> list[go.Scatter3d]:
    traces: list[go.Scatter3d] = []
    for _, row in overlay.features.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        for coords in _iter_geometry_coords(geom):
            xs, ys, zs = [], [], []
            for lon, lat in coords:
                x, y = _lonlat_to_grid(lon, lat, bounds, z.shape)
                xs.append(x)
                ys.append(y)
                zs.append(_sample_z(z, x, y))
            text = _hover_text(row, overlay)
            traces.append(
                go.Scatter3d(
                    x=xs,
                    y=ys,
                    z=zs,
                    mode="lines",
                    name=overlay.name,
                    line={"color": overlay.style.outline, "width": 4},
                    text=[text] * len(xs),
                    hovertemplate="%{text}<extra></extra>",
                    showlegend=False,
                )
            )
    return traces


def _iter_geometry_coords(geom) -> list[list[tuple[float, float]]]:
    geom_type = geom.geom_type
    if geom_type == "LineString":
        return [list(geom.coords)]
    if geom_type == "MultiLineString":
        return [list(part.coords) for part in geom.geoms]
    if geom_type == "Polygon":
        return [list(geom.exterior.coords)]
    if geom_type == "MultiPolygon":
        return [list(part.exterior.coords) for part in geom.geoms]
    if geom_type == "Point":
        return [[(geom.x, geom.y)]]
    if geom_type == "MultiPoint":
        return [[(part.x, part.y)] for part in geom.geoms]
    return []


def _lonlat_to_grid(lon: float, lat: float, bounds: Bounds, shape: tuple[int, int]) -> tuple[float, float]:
    height, width = shape
    x = (lon - bounds.min_lon) / bounds.width * (width - 1)
    y = (bounds.max_lat - lat) / bounds.height * (height - 1)
    return x, y


def _sample_z(z: np.ndarray, x: float, y: float) -> float:
    col = int(np.clip(round(x), 0, z.shape[1] - 1))
    row = int(np.clip(round(y), 0, z.shape[0] - 1))
    value = float(z[row, col])
    return value if np.isfinite(value) else 0.0


def _hover_text(row, overlay: VectorOverlay) -> str:
    parts = [overlay.name]
    for field_name in overlay.hover_fields:
        if field_name in row:
            parts.append(f"{field_name}: {row[field_name]}")
    if overlay.label_column and overlay.label_column in row:
        parts.insert(0, str(row[overlay.label_column]))
    return "<br>".join(parts)
