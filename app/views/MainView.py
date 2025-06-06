from nicegui import ui

from app.viewmodels.MapViewModel import MapViewModel
from nicemvvm.controls.Label import Label
from nicemvvm.controls.LeafletMap import LeafletMap


class MainView:
    def __init__(self):
        view_model = MapViewModel()

        with ui.splitter().classes("w-full h-screen") as splitter:
            with splitter.before:
                ui.label('This is some content on the left hand side.')
                Label().bind(view_model, "center_text", "text")

                with ui.row():
                    Label("Zoom:")
                    Label().bind(view_model, "zoom", "text")
            with splitter.after:
                (LeafletMap().classes("h-full")
                    .bind(view_model, "zoom", "zoom")
                    .bind(view_model, "center", "center")
                )
