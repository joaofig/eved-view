import asyncio
from typing import Self, Tuple, List, Dict, Any
from dataclasses import dataclass, field

from nicegui import ui
from nicegui.elements.leaflet_layers import GenericLayer
from nicegui.events import GenericEventArguments

from nicemvvm.observables.Observable import Observable, Observer, ObserverHandler, ConverterFunction
from nicemvvm.observables.ObservableCollections import ObservableList


@dataclass
class LatLng:
    lat: float
    lng: float
    alt: float = 0.0

    def to_list(self) -> List[float]:
        return [self.lat, self.lng]


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

    @staticmethod
    def from_dict(d: Dict) -> 'Path':
        return Path(**d)

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
    points: List[List[float]] = field(default_factory=list)
    smooth_factor: float = 1.0
    no_clip: bool = False

    @staticmethod
    def from_dict(d: Dict) -> 'Polyline':
        return Polyline(**d)

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
        self._outbound_handler("center", center)

    def _on_map_zoom(self, e: GenericEventArguments):
        zoom = e.args["zoom"]
        self._outbound_handler("zoom", zoom)

    @property
    def polylines(self) -> List[GenericLayer]:
        return self._polylines

    @polylines.setter
    def polylines(self, polylines: List[GenericLayer]) -> None:
        self._polylines = polylines
        for polyline in polylines:
            self.add_layer(polyline)

    def _polylines_handler(self, action: str, args: Dict[str, Any]) -> None:
        match action:
            case "append":
                polyline = args["value"]
                layer = self.generic_layer(**polyline.to_layer())

    def bind(self,
             source: Observable,
             property_name: str,
             local_name: str,
             handler: ObserverHandler|None = None,
             converter: ConverterFunction|None = None) -> Self:

        match local_name:
            case "zoom":
                self.on("map-zoomend", self._on_map_zoom)
                handler = self._inbound_handler
            case "center":
                self.on("map-moveend", self._on_map_move)
                handler = self._inbound_handler
            case "polylines":
                polylines = getattr(source, property_name)
                if isinstance(polylines, ObservableList):
                    obs_list: ObservableList[Polyline] = polylines
                    obs_list.register(self._polylines_handler)
                return self

        Observer.bind(self, source, property_name, local_name,
                      handler, converter)
        return self

    def invalidate_size(self, animate: bool = False) -> Self:
        self.run_map_method("invalidateSize", animate)
        return self

    def fit_bounds(self, bounds: List[LatLng], options: Dict|None = None) -> Self:
        if len(bounds) > 0:
            min_lat = min(b.lat for b in bounds)
            max_lat = max(b.lat for b in bounds)
            min_lng = min(b.lng for b in bounds)
            max_lng = max(b.lng for b in bounds)
            bounds_list = [[min_lat, min_lng], [max_lat, max_lng]]
            self.run_map_method("fitBounds",bounds_list, options)
        return self

    def polyline(self,
                 points: List[Tuple[float, float]],
                 props: Dict|None = None
    ) -> GenericLayer:
        return self.generic_layer(name="polyline", args=[points, props])
