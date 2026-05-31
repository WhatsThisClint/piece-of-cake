"""Small geometry-free bounding box helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Bounds:
    """A WGS84 bounding box.

    Coordinates are stored as longitude/latitude degrees.
    """

    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    def __post_init__(self) -> None:
        if self.min_lon >= self.max_lon:
            raise ValueError("min_lon must be smaller than max_lon")
        if self.min_lat >= self.max_lat:
            raise ValueError("min_lat must be smaller than max_lat")
        if not (-180 <= self.min_lon <= 180 and -180 <= self.max_lon <= 180):
            raise ValueError("longitude values must be in WGS84 degrees")
        if not (-90 <= self.min_lat <= 90 and -90 <= self.max_lat <= 90):
            raise ValueError("latitude values must be in WGS84 degrees")

    @classmethod
    def from_center(cls, lon: float, lat: float, buffer_degrees: float) -> "Bounds":
        """Create a square-ish bounding box around a center point."""

        if buffer_degrees <= 0:
            raise ValueError("buffer_degrees must be positive")
        return cls(
            min_lon=lon - buffer_degrees,
            min_lat=lat - buffer_degrees,
            max_lon=lon + buffer_degrees,
            max_lat=lat + buffer_degrees,
        )

    @classmethod
    def from_tuple(cls, value: tuple[float, float, float, float]) -> "Bounds":
        """Build from ``(min_lon, min_lat, max_lon, max_lat)``."""

        return cls(*value)

    @property
    def width(self) -> float:
        return self.max_lon - self.min_lon

    @property
    def height(self) -> float:
        return self.max_lat - self.min_lat

    @property
    def center(self) -> tuple[float, float]:
        return (
            self.min_lon + self.width / 2,
            self.min_lat + self.height / 2,
        )

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.min_lon, self.min_lat, self.max_lon, self.max_lat)

