from typing import Any

from nicegui import ui

from app.commands.map import AddToMapCommand
from app.viewmodels.MapViewModel import MapViewModel
from app.views.MapView import MapView
from app.views.TripView import TripView
from nicemvvm import nm
from nicemvvm.ValueConverter import ValueConverter


class LatLngTextConverter(ValueConverter):
    def convert(self, v: Any) -> Any:
        return f"({v[0]}, {v[1]})"


class MainView:
    def __init__(self):
        view_model = MapViewModel()

        with ui.splitter(value=30).classes("w-full h-screen p-0") as splitter:
            with splitter.before:
                TripView(view_model)

                ui.label("Center:")
                nm.label().bind(
                    view_model,
                    "center",
                    "text",
                    converter=LatLngTextConverter(),
                )
                # ui.label("Zoom:")
                # nm.label().bind(view_model, "zoom", "text")
                # ui.label("Selected Trip ID:")
                # nm.label().bind(view_model, "selected_trip_id", "text")

                with ui.row():
                    (
                        nm.button(
                            "Add GPS",
                            command=AddToMapCommand(view_model, trace_name="gps"),
                        )
                        .props("size=sm no-caps")
                        .disable()
                    )
                    (
                        nm.button(
                            "Add Match",
                            command=AddToMapCommand(view_model, trace_name="match"),
                        )
                        .props("size=sm no-caps")
                        .disable()
                    )
                    (
                        nm.button(
                            "Add Nodes",
                            command=AddToMapCommand(view_model, trace_name="nodes"),
                        )
                        .props("size=sm no-caps")
                        .disable()
                    )

            with splitter.after:
                MapView(view_model)
