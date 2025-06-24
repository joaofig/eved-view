from typing import Dict

from nicegui import ui


class LeafletMap:
    def __init__(
        self,
        zoom: int = 3,
        classes: str = "h-full w-full",
        options: Dict | None = None,
        draw_control: Dict | None = None,
    ) -> None:
        self.map = ui.leaflet(zoom=zoom, options=options, draw_control=draw_control)

        if len(classes) > 0:
            self.map.classes(classes)
