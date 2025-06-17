from nicegui import ui
from nicemvvm import nm

from app.viewmodels.MapViewModel import MapViewModel
from app.views.TripView import TripView


class MainView:
    def __init__(self):
        view_model = MapViewModel()

        with ui.splitter().classes("w-full h-screen") as splitter:
            with splitter.before:
                TripView(view_model)

                ui.label("Center:")
                nm.label().bind(view_model, "center_text", "text")
                ui.label("Zoom:")
                nm.label().bind(view_model, "zoom", "text")
                ui.label("Selected Trip ID:")
                nm.label().bind(view_model, "selected_trip_id", "text")

                ui.button("Test").props("size=sm")

            with splitter.after:
                self.m = (nm.leaflet()
                            .classes("h-full w-full")
                            .bind(view_model, "zoom", "zoom")
                            .bind(view_model, "center", "center"))

            # Make sure the map is correctly resized
            splitter.on_value_change(lambda _: self.m.invalidate_size(animate=True))
            splitter.on("resize", lambda _: self.m.invalidate_size(animate=True))
