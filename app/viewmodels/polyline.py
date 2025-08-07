from typing import List

from app.viewmodels.shape import MapShape
from nicemvvm.controls.leaflet.types import LatLng, GeoBounds
from nicemvvm.observables.observability import notify_change


class MapPolyline(MapShape):
    def __init__(
        self,
        shape_id: str,
        traj_id: int,
        vehicle_id: int,
        km: float,
        color: str,
        weight: float,
        opacity: float,
        trace_name: str,
        locations: List[LatLng],
        dash_array: str = "",
        dash_offset: str = "",
    ):
        super().__init__(
            shape_id,
            color=color,
            weight=weight,
            opacity=opacity,
            fill=False,
            fill_color=color,
            fill_opacity=opacity,
            dash_array=dash_array,
            dash_offset=dash_offset
        )
        self._traj_id = traj_id
        self._vehicle_id = vehicle_id
        self._km = km
        self._trace_name = trace_name
        self._locations = locations
        self._bounds: GeoBounds | None = None

    @property
    def traj_id(self) -> int:
        return self._traj_id

    @property
    def vehicle_id(self) -> int:
        return self._vehicle_id

    @property
    def km(self):
        return self._km

    @property
    def trace_name(self) -> str:
        return self._trace_name

    @trace_name.setter
    @notify_change
    def trace_name(self, value: str):
        self._trace_name = value

    @property
    def locations(self) -> List[LatLng]:
        return self._locations

    @locations.setter
    @notify_change
    def locations(self, value: List[LatLng]):
        self._locations = value

    def get_bounds(self) -> GeoBounds:
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
            "traj_id": self._traj_id,
            "vehicle_id": self._vehicle_id,
            "color": self._color,
            "weight": self._weight,
            "opacity": self._opacity,
            "trace_name": self._trace_name,
            "locations": self._locations,
            "km": self._km,
            "dash_array": self._dash_array,
            "dash_offset": self._dash_offset,
        }
