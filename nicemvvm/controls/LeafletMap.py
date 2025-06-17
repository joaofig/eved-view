from typing import Self, Tuple, List, Dict
from dataclasses import dataclass, field

from nicegui import ui
from nicegui.elements.leaflet_layers import GenericLayer
from nicegui.events import GenericEventArguments

from nicemvvm.observables.Observable import Observable, Observer, ObserverHandler


@dataclass
class LatLng:
    lat: float
    lng: float
    alt: float = 0.0


@dataclass
class Path:
    stroke: bool = True
    color: str = "#3388ff"
    opacity: float = 1.0
    weight: float = 3.0
    line_cap: str = "round"
    line_join: str = "round"
    dash_array: str = ""
    dash_offset: int = 0
    fill: bool = False
    fill_color: str = "#3388ff"
    fill_opacity: float = 0.2
    fill_rule: str = "evenodd"

    def to_dict(self):
        return {
            "stroke": self.stroke,
            "color": self.color,
            "opacity": self.opacity,
            "weight": self.weight,
            "lineCap": self.line_cap,
            "lineJoin": self.line_join,
            "dashArray": self.dash_array,
            "dashOffset": self.dash_offset,
            "fill": self.fill,
            "fillColor": self.fill_color,
            "fillOpacity": self.fill_opacity,
            "fillRule": self.fill_rule,
        }


@dataclass
class Polyline(Path):
    points: List[LatLng] = field(default_factory=list)
    smooth_factor: float = 1.0
    no_clip: bool = False

    def to_dict(self):
        return {
            "smoothFactor": self.smooth_factor,
            "noClip": self.no_clip,
            "points": [[l.lat, l.lng] for l in self.points]
        } | Path.to_dict(self)


@dataclass
class Polygon(Polyline):
    ...



class LeafletMap(ui.leaflet, Observer):
    def __init__(self):
        ui.leaflet.__init__(self)
        Observer.__init__(self)

        self._polylines: List[GenericLayer] = []

    def _on_map_move(self, e: GenericEventArguments):
        center = e.args["center"]
        zoom = e.args["zoom"]
        self._outbound_handler("zoom", zoom)
        self._outbound_handler("center", center)

    @property
    def polylines(self) -> List[GenericLayer]:
        return self._polylines

    @polylines.setter
    def polylines(self, polylines: List[GenericLayer]) -> None:
        self._polylines = polylines
        for polyline in polylines:
            self.add_layer(polyline)

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
    #
    # def polyline(self,
    #              points: List[Tuple[float, float]],
    #              props: Dict|None = None
    # ) -> GenericLayer:
    #     return Leaflet.generic_layer(name="polyline", args=[points, props])
