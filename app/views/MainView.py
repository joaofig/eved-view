from nicegui import ui
from nicemvvm import nm
from app.views.MapView import MapView
from app.viewmodels.MapViewModel import MapViewModel
from app.views.TripView import TripView


class MainView:
    def __init__(self):
        view_model = MapViewModel()

        with ui.splitter(value=30).classes("w-full h-screen p-0") as splitter:
            with splitter.before:
                TripView(view_model)

                ui.label("Center:")
                nm.label().bind(view_model, "center_text", "text")
                ui.label("Zoom:")
                nm.label().bind(view_model, "zoom", "text")
                ui.label("Selected Trip ID:")
                nm.label().bind(view_model, "selected_trip_id", "text")

                nm.button("Test").props("size=md no-caps")

            with splitter.after:
                MapView(view_model)
