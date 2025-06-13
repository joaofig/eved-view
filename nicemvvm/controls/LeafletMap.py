from typing import Self
from dataclasses import dataclass

from nicegui.elements.leaflet import Leaflet
from nicegui.events import GenericEventArguments

from nicemvvm.observables.Observable import Observable, Observer, ObserverHandler


@dataclass
class LatLng:
    lat: float
    lng: float
    alt: float = 0.0


class LeafletMap(Leaflet, Observer):
    def __init__(self):
        Leaflet.__init__(self)
        Observer.__init__(self)

    def _on_map_move(self, e: GenericEventArguments):
        center = e.args["center"]
        zoom = e.args["zoom"]
        self._outbound_handler("zoom", zoom)
        self._outbound_handler("center", center)

    def bind(self,
             source: Observable,
             property_name: str,
             local_name: str,
             handler: ObserverHandler|None = None) -> Self:

        match local_name:
            case "zoom":
                self.on("map-zoom", self._on_map_move)
                source.register(self._inbound_handler)
            case "center":
                self.on("map-move", self._on_map_move)
                source.register(self._inbound_handler)

        Observer.bind(self, source, property_name, local_name, handler)
        return self

    def invalidate_size(self, animate: bool = False):
        self.run_map_method("invalidateSize", animate)

