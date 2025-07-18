from typing import List

from app.viewmodels.shape import MapShape
from nicemvvm.controls.leaflet.types import LatLng
from nicemvvm.observables.observability import notify_change, Observable


class MapCircle(MapShape, Observable):
    def __init__(self, shape_id: str, color: str, weight: float, opacity: float, center: LatLng, radius: float,
                 fill: bool, fill_color: str, fill_opacity: float):
        super().__init__(shape_id, color, weight, opacity, fill, fill_color, fill_opacity)
        self._center = center
        self._radius = radius

    @property
    def center(self) -> LatLng:
        return self._center

    @property
    def radius(self) -> float:
        return self._radius

    @center.setter
    @notify_change
    def center(self, value: LatLng):
        self._center = value

    @radius.setter
    @notify_change
    def radius(self, value: float):
        self._radius = value