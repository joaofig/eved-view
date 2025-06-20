from typing import Tuple, Any, Mapping

from app.models.TripModel import TripModel, Trip
from nicemvvm.Command import Command
from nicemvvm.observables.Observable import Observable, notify, Observer
from nicemvvm.ResourceLocator import ResourceLocator
from nicemvvm.observables.ObservableCollections import ObservableList


class MapViewModel(Observable):
    def __init__(self):
        super().__init__()
        self._zoom = 10
        self._center: Tuple[float,float] = (0.0, 0.0)
        self._center_text: str = "(0, 0)"
        self._locator = ResourceLocator()
        self._trip_model: TripModel = self._locator["TripModel"]
        self._trips: ObservableList = ObservableList(self._trip_model.load())
        self._selected_trip: Trip|None = None
        self._selected_trip_id: str = ""

    @property
    def zoom(self) -> int:
        return self._zoom

    @zoom.setter
    @notify
    def zoom(self, value: int) -> None:
        self._zoom = value

    @property
    def center(self) -> Tuple[float,float]:
        return self._center

    @center.setter
    @notify
    def center(self, value: Tuple[float,float]) -> None:
        self._center = value
        self.center_text = f"({self.center[0]}, {self.center[1]})"

    @property
    def center_text(self) -> str:
        return self._center_text

    @center_text.setter
    @notify
    def center_text(self, text: str) -> None:
        self._center_text = text

    @property
    def trips(self) -> ObservableList:
        return self._trips

    @property
    def selected_trip(self) -> Trip|None:
        return self._selected_trip

    @selected_trip.setter
    @notify
    def selected_trip(self, trip: Trip|None) -> None:
        self._selected_trip = trip
        if trip is not None:
            self.selected_trip_id = str(trip.traj_id)
        else:
            self.selected_trip_id = ""

    @property
    def selected_trip_id(self) -> str:
        return self._selected_trip_id

    @selected_trip_id.setter
    @notify
    def selected_trip_id(self, trip_id: str) -> None:
        self._selected_trip_id = trip_id


class AddToMapCommand(Command):
    def __init__(self, view_model: MapViewModel):
        super().__init__()
        self._view_model = view_model
        view_model.register(self._handler)
        self.is_enabled = False

    def _handler(self,
                 action: str,
                 args: Mapping[str, Any]) -> None:
        if action == "property":
            name = args["name"]
            value = args["value"]
            if name == "selected_trip":
                self.is_enabled = (value is not None)

    def run(self, arg: Any = None) -> Any:
        trip = self._view_model.selected_trip
        if trip is not None:
            if len(trip.signals) == 0:
                trip.load_signals()
            if len(trip.nodes) == 0:
                trip.load_nodes()
        return None