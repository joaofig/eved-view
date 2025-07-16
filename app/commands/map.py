from typing import Any

from app.viewmodels.MapViewModel import MapViewModel, SelectedTripValueConverter
from nicemvvm.Command import Command
from nicemvvm.observables.Observable import Observer


class AddRouteToMapCommand(Command, Observer):
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

    def execute(self, arg: Any = None) -> Any:
        trip = self._view_model.selected_trip
        if trip is not None:
            if len(trip.signals) == 0:
                trip.load_signals()
            if len(trip.nodes) == 0:
                trip.load_nodes()
            self._view_model.show_polyline(trip, self._trace_name)
        return None
