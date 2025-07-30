from app.geo.geomath import num_haversine, delta_location
from app.viewmodels.shape import MapShape
from nicemvvm.controls.leaflet.types import LatLng, GeoBounds
from nicemvvm.observables.observability import Observable, notify_change


class MapCircle(MapShape, Observable):
    def __init__(
        self,
        shape_id: str,
        color: str,
        weight: float,
        opacity: float,
        center: LatLng,
        radius: float,
        fill: bool,
        fill_color: str,
        fill_opacity: float,
        dash_array: str = "",
        dash_offset: str = "",
    ):
        super().__init__(
            shape_id, color, weight, opacity, fill, fill_color, fill_opacity,
            dash_array=dash_array,
            dash_offset=dash_offset,
        )
        self._center = center
        self._radius = radius
        self._bounds: GeoBounds | None = None

    def contains(self, latlng: LatLng) -> bool:
        d = num_haversine(self._center.lat, self._center.lng, latlng.lat, latlng.lng)
        return d <= self._radius

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

    @property
    def bounds(self) -> GeoBounds:
        if not self._bounds:
            lat = self._center.lat
            lng = self._center.lng
            radius = self._radius
            n = delta_location(lat, lng, 0.0, radius)
            e = delta_location(lat, lng, 90.0, radius)
            s = delta_location(lat, lng, 180.0, radius)
            w = delta_location(lat, lng, 270.0, radius)
            self._bounds = GeoBounds(LatLng(s[0], w[1]), LatLng(n[0], e[1]))
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
            "center": self._center.to_dict(),
            "radius": self._radius,
            "dash_array": self._dash_array,
            "dash_offset": self._dash_offset,
        }
