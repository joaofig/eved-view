from typing import Any, List, Tuple

from app.models.TripModel import Trip, TripModel
from nicemvvm.Command import Command
from nicemvvm.controls.LeafletMap import LatLng
from nicemvvm.observables.Observable import Observable, Observer, notify_change
from nicemvvm.observables.ObservableCollections import ObservableList
from nicemvvm.ResourceLocator import ResourceLocator
from nicemvvm.ValueConverter import ValueConverter


class MapPolyline(Observable):
    def __init__(
        self,
        polyline_id: str,
        traj_id: int,
        vehicle_id: int,
        km: float,
        is_visible: bool,
        color: str,
        weight: float,
        opacity: float,
        trace_name: str,
        locations: List[LatLng],
    ):
        super().__init__()
        self._polyline_id = polyline_id
        self._traj_id = traj_id
        self._vehicle_id = vehicle_id
        self._km = km
        self._is_visible = is_visible
        self._color = color
        self._weight = weight
        self._opacity = opacity
        self._trace_name = trace_name
        self._locations = locations

    @property
    def polyline_id(self) -> str:
        return self._polyline_id

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
    def is_visible(self) -> bool:
        return self._is_visible

    @is_visible.setter
    @notify_change
    def is_visible(self, value: bool):
        self._is_visible = value

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    @notify_change
    def color(self, value: str):
        self._color = value

    @property
    def weight(self) -> float:
        return self._weight

    @weight.setter
    @notify_change
    def weight(self, value: float):
        self._weight = value

    @property
    def opacity(self) -> float:
        return self._opacity

    @opacity.setter
    @notify_change
    def opacity(self, value: float):
        self._opacity = value

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

    def to_dict(self):
        return {
            "polyline_id": self._polyline_id,
            "traj_id": self._traj_id,
            "vehicle_id": self._vehicle_id,
            "is_visible": self._is_visible,
            "color": self._color,
            "weight": self._weight,
            "opacity": self._opacity,
            "trace_name": self._trace_name,
            "locations": self._locations,
            "km": self._km,
        }


class MapViewModel(Observable):
    def __init__(self):
        super().__init__()
        self._zoom = 10
        self._center: Tuple[float, float] = (0.0, 0.0)
        self._center_text: str = "(0, 0)"
        self._locator = ResourceLocator()
        self._trip_model: TripModel = self._locator["TripModel"]
        self._trips: ObservableList[Trip] = ObservableList(self._trip_model.load())
        self._selected_trip: Trip | None = None
        self._selected_trip_id: str = ""
        self._selected_polyline: MapPolyline | None = None
        self._polylines: ObservableList[MapPolyline] = ObservableList()
        self._bounds: List[LatLng] = list()

    def _has_trace(self, trip: Trip, trace_name: str) -> bool:
        return any(
            t
            for t in self._polylines
            if t.traj_id == trip.traj_id and t.trace_name == trace_name
        )

    def show_polyline(self, trip: Trip, trace_name: str) -> None:
        if not self._has_trace(trip, trace_name):
            match trace_name:
                case "gps":
                    color = "#0000FF"
                    locations = [LatLng(p.lat, p.lon) for p in trip.signals]
                case "match":
                    color = "#FF0000"
                    locations = [LatLng(p.match_lat, p.match_lon) for p in trip.signals]
                case "nodes":
                    color = "#00FF00"
                    locations = [LatLng(n.lat, n.lon) for n in trip.nodes]
                case _:
                    locations = []
                    color = "#000000"

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
            # self.selected_polyline = poly
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
    def trips(self) -> ObservableList[Trip]:
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
    def selected_polyline(self) -> MapPolyline | None:
        return self._selected_polyline

    @selected_polyline.setter
    @notify_change
    def selected_polyline(self, polyline: MapPolyline | None):
        self._selected_polyline = polyline

    @property
    def bounds(self) -> List[LatLng]:
        return self._bounds

    @bounds.setter
    @notify_change
    def bounds(self, value: List[LatLng]) -> None:
        self._bounds = value


class SelectedTripValueConverter(ValueConverter):
    def __init__(self):
        super().__init__()

    def convert(self, x: Any) -> Any:
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
