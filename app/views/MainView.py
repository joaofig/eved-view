from nicegui import ui

from app.viewmodels.MapViewModel import MapViewModel
from app.views.TripView import TripView
from nicemvvm.controls.Label import Label
from nicemvvm.controls.LeafletMap import LeafletMap


class MainView:
    def __init__(self):
        view_model = MapViewModel()

        with ui.splitter().classes("w-full h-screen") as splitter:
            with splitter.before:
                TripView(view_model)

                Label("Center:")
                Label().bind(view_model, "center_text", "text")
                Label("Zoom:")
                Label().bind(view_model, "zoom", "text")
                Label("Selected Trip ID:")
                Label().bind(view_model, "selected_trip_id", "text")

            with splitter.after:
                self.m = (LeafletMap()
                            .classes("h-full w-full")
                            .bind(view_model, "zoom", "zoom")
                            .bind(view_model, "center", "center"))

            # Make sure the map is correctly resized
            splitter.on_value_change(lambda _: self.m.invalidate_size(animate=True))
            splitter.on("resize", lambda _: self.m.invalidate_size(animate=True))
