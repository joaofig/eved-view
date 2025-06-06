from nicegui import ui

from nicemvvm.controls.LeafletMap import LeafletMap


class MainView:
    def __init__(self):
        with ui.splitter().classes("w-full h-screen") as splitter:
            with splitter.before:
                ui.label('This is some content on the left hand side.')
            with splitter.after:
                LeafletMap().classes("h-full")
