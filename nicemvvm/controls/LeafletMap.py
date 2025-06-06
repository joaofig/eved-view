from typing import Tuple, Any, Dict, Callable

from nicegui import ui
from nicegui.elements.leaflet import Leaflet
from nicegui.events import GenericEventArguments

from nicemvvm.Observable import Observable


class LeafletMap(Leaflet):
    def __init__(self, center: Tuple[float, float] = (0.0, 0.0), zoom: int = 5,):
        Leaflet.__init__(self, center, zoom)

        self.bind_source: Observable|None = None

        self.on("map-zoom", self._on_map_zoom)
        self.on("map-move", self._on_map_move)

        self._bindings: Dict[str, Callable] = {
            "center": self._handle_center,
            "zoom": self._handle_zoom,
        }
        self._prop_map = dict()

    def _on_map_zoom(self, e: GenericEventArguments):
        print(e)

    def _on_map_move(self, e: GenericEventArguments):
        print(e)
        # self.zoom = e.args["value"]

    def _handle_center(self, value: Any) -> None:
        ...

    def _handle_zoom(self, value: Any) -> None:
        if isinstance(value, int):
            self.zoom = value

    def _bind_handler(self, source: object, name: str, value: Any) -> None:
        if name in self._prop_map:
            local_name = self._prop_map[name]
            self._bindings[local_name](value)

    def bind(self,
             local_name: str,
             prop_name: str,
             source: Observable|None = None) -> None:
        if local_name not in self._bindings:
            raise ValueError(f"No handler for {local_name}")

        self._prop_map[prop_name] = local_name

        if source is not None:
            source.bind(self._bind_handler)
            if self.bind_source is None:
                self.bind_source = source
        elif self.bind_source is not None:
            self.bind_source.unbind(self._bind_handler)
