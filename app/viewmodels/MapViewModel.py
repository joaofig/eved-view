from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from app.models.TripModel import Trip, TripModel
from nicemvvm.Command import Command
from nicemvvm.controls.LeafletMap import LatLng
from nicemvvm.observables.Observable import Observable, Observer, notify_change
from nicemvvm.observables.ObservableCollections import ObservableList
from nicemvvm.ResourceLocator import ResourceLocator
from nicemvvm.ValueConverter import ValueConverter


@dataclass
class MapPolyline:
    polyline_id: str
    traj_id: int
    vehicle_id: int
    is_visible: bool
    color: str
    weight: float
    opacity: float
    trace_name: str
    km: float
    locations: List[LatLng] = field(default_factory=list)

    def to_layer(self) -> Dict[str, Any]:
        return {
            "name": "polyline",
            "args": [
                [[p.lat, p.lng] for p in self.locations],
                {"color": self.color, "weight": self.weight, "opacity": self.opacity},
            ],
        }

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "id": f"{self.traj_id}_{self.trace_name}",
            "layer": self.to_layer(),
            "data": {
                "visible": self.is_visible,
                "traj_id": self.traj_id,
                "vehicle_id": self.vehicle_id,
                "trace_name": self.trace_name,
            },
        }
        return d


class MapViewModel(Observable):
    def __init__(self):
        super().__init__()
        self._zoom = 10
        self._center: Tuple[float, float] = (0.0, 0.0)
        self._center_text: str = "(0, 0)"
        self._locator = ResourceLocator()
        self._trip_model: TripModel = self._locator["TripModel"]
        self._trips: ObservableList = ObservableList(self._trip_model.load())
        self._selected_trip: Trip | None = None
        self._selected_trip_id: str = ""
        self._selected_polylines: ObservableList[MapPolyline] = ObservableList()
        self._polylines: ObservableList[MapPolyline] = ObservableList()
        self._bounds: List[LatLng] = list()

    def _has_trace(self, trip: Trip, trace_name: str) -> bool:
        n = len(
            [
                t
                for t in self._polylines
                if t.traj_id == trip.traj_id and t.trace_name == trace_name
            ]
        )
        return n > 0

    def show_polyline(self, trip: Trip, trace_name: str) -> None:
        if not self._has_trace(trip, trace_name):
            match trace_name:
                case "gps":
                    color = "blue"
                    locations = [LatLng(p.lat, p.lon) for p in trip.signals]
                case "match":
                    color = "red"
                    locations = [LatLng(p.match_lat, p.match_lon) for p in trip.signals]
                case "nodes":
                    color = "gray"
                    locations = [LatLng(n.lat, n.lon) for n in trip.nodes]
                case _:
                    locations = []
                    color = "black"

            poly = MapPolyline(
                polyline_id=f"{trip.traj_id}_{trace_name}",
                traj_id=trip.traj_id,
                vehicle_id=trip.vehicle_id,
                is_visible=True,
                color=color,
                weight=3.0,
                opacity=0.6,
                trace_name=trace_name,
                locations=locations,
                km=trip.km,
            )
            self._polylines.append(poly)
            self._selected_polylines.append(poly)
            self.bounds = locations

    @property
    def zoom(self) -> int:
        return self._zoom

    @zoom.setter
    @notify_change
    def zoom(self, value: int) -> None:
        self._zoom = value

    @property
    def center(self) -> Tuple[float, float]:
        return self._center

    @center.setter
    @notify_change
    def center(self, value: Tuple[float, float]) -> None:
        self._center = value

    @property
    def trips(self) -> ObservableList:
        return self._trips

    @property
    def selected_trip(self) -> Trip | None:
        return self._selected_trip

    @selected_trip.setter
    @notify_change
    def selected_trip(self, trip: Trip | None) -> None:
        self._selected_trip = trip
        if trip is not None:
            self.selected_trip_id = str(trip.traj_id)
        else:
            self.selected_trip_id = ""

    @property
    def selected_trip_id(self) -> str:
        return self._selected_trip_id

    @selected_trip_id.setter
    @notify_change
    def selected_trip_id(self, trip_id: str) -> None:
        self._selected_trip_id = trip_id

    @property
    def polylines(self) -> ObservableList[MapPolyline]:
        return self._polylines

    @property
    def selected_polylines(self) -> ObservableList[MapPolyline]:
        return self._selected_polylines

    @property
    def bounds(self) -> List[LatLng]:
        return self._bounds

    @bounds.setter
    @notify_change
    def bounds(self, value: List[LatLng]) -> None:
        self._bounds = value


class SelectedTripValueConverter(ValueConverter):
    @staticmethod
    def convert(x: Any) -> Any:
        return x is not None


class AddToMapCommand(Command, Observer):
    def __init__(self, view_model: MapViewModel, trace_name: str, **kwargs):
        self._view_model = view_model
        self._trace_name = trace_name
        super().__init__(is_enabled=False, **kwargs)
        self.bind(
            view_model,
            property_name="selected_trip",
            local_name="is_enabled",
            converter=SelectedTripValueConverter(),
        )

    def run(self, arg: Any = None) -> Any:
        trip = self._view_model.selected_trip
        if trip is not None:
            if len(trip.signals) == 0:
                trip.load_signals()
            if len(trip.nodes) == 0:
                trip.load_nodes()
            self._view_model.show_polyline(trip, self._trace_name)
        return None
