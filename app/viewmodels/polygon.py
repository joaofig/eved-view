from typing import List

from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon

from app.viewmodels.shape import MapShape
from nicemvvm.controls.leaflet.types import LatLng, GeoBounds
from nicemvvm.observables.observability import notify_change


class MapPolygon(MapShape):
    def __init__(
        self,
        shape_id: str,
        color: str,
        weight: float,
        opacity: float,
        locations: List[LatLng],
        fill: bool = True,
        fill_color: str = "",
        fill_opacity: float = 0.2,
        dash_array: str = "",
        dash_offset: str = "",
    ):
        super().__init__(
            shape_id=shape_id,
            color=color,
            weight=weight,
            opacity=opacity,
            fill=fill,
            fill_color=color if not fill_color else fill_color,
            fill_opacity=fill_opacity,
            dash_array=dash_array,
            dash_offset=dash_offset,
        )
        self._locations = locations
        self._bounds: GeoBounds | None = None

    def contains(self, latlng: LatLng) -> bool:
        point = Point(latlng.lng, latlng.lat)
        polygon = Polygon([ll.lng, ll.lat] for ll in self._locations)
        return polygon.contains(point)

    @property
    def locations(self) -> List[LatLng]:
        return self._locations

    @locations.setter
    @notify_change
    def locations(self, value: List[LatLng]):
        self._locations = value

    @property
    def bounds(self) -> GeoBounds:
        if not self._bounds:
            self._bounds = GeoBounds(
                LatLng(min((p.lat for p in self._locations)),
                       min((p.lng for p in self._locations))),
                LatLng(max((p.lat for p in self._locations)),
                       max((p.lng for p in self._locations))))
        return self._bounds

    def to_dict(self):
        return {
            "shape_id": self._shape_id,
            "color": self._color,
            "weight": self._weight,
            "opacity": self._opacity,
            "fill": self._fill,
            "fill_color": self._fill_color,
            "fill_opacity": self._fill_opacity,
            "vertices": len(self._locations),
            "dash_array": self._dash_array,
            "dash_offset": self._dash_offset,
        }
