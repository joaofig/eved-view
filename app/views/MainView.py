from nicegui import ui
from nicemvvm import nm
from app.views.MapView import MapView
from app.viewmodels.MapViewModel import MapViewModel, AddToMapCommand
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

                add_to_map = nm.button("Add to Map").props("size=md no-caps")
                add_to_map.command = AddToMapCommand(view_model)
                add_to_map.disable()

            with splitter.after:
                MapView(view_model)
