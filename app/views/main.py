from typing import Any

from nicegui import ui

from app.converters.general import NotNoneValueConverter
from app.viewmodels.map import MapViewModel
from app.views.map import MapView
from app.views.trip import TripView
from nicemvvm import nm
from nicemvvm.command import RelayCommand
from nicemvvm.converter import ValueConverter


class LatLngTextConverter(ValueConverter):
    def convert(self, v: Any) -> Any:
        return f"({v[0]}, {v[1]})"


class MainView:
    def __init__(self):
        self._view_model = MapViewModel()

        with ui.splitter(value=30).classes("w-full h-screen p-0") as splitter:
            with splitter.before:
                TripView(self._view_model)

                with ui.row():
                    gps_cmd = RelayCommand(lambda arg: self._add_route_to_map("gps"))
                    gps_cmd.bind(
                        self._view_model,
                        property_name="selected_trip",
                        local_name="is_enabled",
                        converter=NotNoneValueConverter(),
                    )
                    nm.button(text="Add GPS", command=gps_cmd).props(
                        "size=sm no-caps"
                    ).disable()

                    match_cmd = RelayCommand(
                        lambda arg: self._add_route_to_map("match")
                    )
                    match_cmd.bind(
                        self._view_model,
                        property_name="selected_trip",
                        local_name="is_enabled",
                        converter=NotNoneValueConverter(),
                    )
                    nm.button(text="Add Match", command=match_cmd).props(
                        "size=sm no-caps"
                    ).disable()

                    node_cmd = RelayCommand(lambda arg: self._add_route_to_map("nodes"))
                    node_cmd.bind(
                        self._view_model,
                        property_name="selected_trip",
                        local_name="is_enabled",
                        converter=NotNoneValueConverter(),
                    )
                    nm.button(text="Add Nodes", command=node_cmd).props(
                        "size=sm no-caps"
                    ).disable()

            with splitter.after:
                MapView(self._view_model)

    def _add_route_to_map(self, trace_name: str) -> None:
        trip = self._view_model.selected_trip
        if trip is not None:
            if len(trip.signals) == 0:
                trip.load_signals()
            if len(trip.nodes) == 0:
                trip.load_nodes()
            self._view_model.show_polyline(trip, trace_name)
