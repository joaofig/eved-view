from nicegui import ui

from app.viewmodels.MapViewModel import MapViewModel
from nicemvvm.controls.LeafletMap import LeafletMap


class MainView:
    def __init__(self):
        view_model = MapViewModel()

        with ui.splitter().classes("w-full h-screen") as splitter:
            with splitter.before:
                ui.label('This is some content on the left hand side.')
            with splitter.after:
                m = LeafletMap().classes("h-full")
                m.bind_zoom(view_model, "zoom")
                m.bind_center(view_model, "center")