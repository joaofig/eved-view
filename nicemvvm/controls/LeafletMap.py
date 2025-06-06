from typing import Tuple, Any, Dict, Callable

from nicegui import ui
from nicegui.elements.leaflet import Leaflet
from nicegui.events import GenericEventArguments

from nicemvvm.Observable import Observable, Observer


class LeafletMap(Leaflet, Observer):
    def __init__(self):
        Leaflet.__init__(self)
        Observer.__init__(self)

    def _on_map_zoom(self, e: GenericEventArguments):
        zoom = e.args["zoom"]
        self._outbound_handler("zoom", zoom)

    def _on_map_move(self, e: GenericEventArguments):
        center = e.args["center"]
        self._outbound_handler("center", center)

    def bind_zoom(self, source: Observable, property_name: str) -> None:
        self.on("map-zoom", self._on_map_zoom)

        source.register(property_name, self._inbound_handler)
        self.bind(source, property_name, "zoom")

    def bind_center(self, source: Observable, property_name: str) -> None:
        self.on("map-move", self._on_map_move)

        source.register(property_name, self._inbound_handler)
        self.bind(source, property_name, "center")
