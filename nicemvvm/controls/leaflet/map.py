from typing import Union, Dict, Any, Self, List

from nicegui import ui
from nicegui.events import GenericEventArguments

from nicemvvm.ValueConverter import ValueConverter
from nicemvvm.controls.leaflet.polygon import Polygon
from nicemvvm.controls.leaflet.polyline import Polyline
from nicemvvm.controls.leaflet.types import LatLng
from nicemvvm.observables.Observable import Observer, Observable, ObserverHandler
from nicemvvm.observables.ObservableCollections import ObservableList


class LeafletMap(ui.leaflet, Observer):
    def __init__(
        self,
        draw_control: Union[bool, Dict] = False,
        hide_drawn_items: bool = False,
    ):
        ui.leaflet.__init__(
            self, draw_control=draw_control, hide_drawn_items=hide_drawn_items
        )
        Observer.__init__(self)

        self._polylines: Dict[str, Polyline] = {}
        self._polyline_converter: ValueConverter | None = None
        self._polygons: Dict[str, Polygon] = {}
        self._polygon_converter: ValueConverter | None = None

    def _on_map_move(self, e: GenericEventArguments):
        center = e.args["center"]
        self._outbound_handler("center", center)

    def _on_map_zoom(self, e: GenericEventArguments):
        zoom = e.args["zoom"]
        self._outbound_handler("zoom", zoom)

    def _polygons_handler(self, action: str, args: Dict[str, Any]) -> None:
        def to_polygon(v: Any) -> Polygon:
            p: Polyline = (
                value
                if self._polygon_converter is None
                else self._polygon_converter.convert(v)
            )
            return p

        def add_polygon(v: Any) -> Polygon:
            p: Polygon = to_polygon(v)
            if p.layer_id not in self._polygons:
                p.add_to(self)
                self._polygons[p.layer_id] = p
            return p

        match action:
            case "append":
                add_polygon(args["value"])

            case "extend":
                for value in args["values"]:
                    add_polygon(value)

            case "pop" | "remove":
                polygon = to_polygon(args["value"])
                layer = self._polylines[polygon.layer_id]
                layer.remove()
                del self._polylines[polygon.layer_id]

            case "clear":
                for layer_id, layer in self._polygons.items():
                    layer.remove()
                self._polygons.clear()

    def _polylines_handler(self, action: str, args: Dict[str, Any]) -> None:
        def to_polyline(v: Any) -> Polyline:
            p: Polyline = (
                value
                if self._polyline_converter is None
                else self._polyline_converter.convert(v)
            )
            return p

        def add_polyline(v: Any) -> Polyline:
            p: Polyline = to_polyline(v)
            if p.layer_id not in self._polylines:
                p.add_to(self)
                self._polylines[p.layer_id] = p
            return p

        match action:
            case "append":
                add_polyline(args["value"])

            case "extend":
                for value in args["values"]:
                    add_polyline(value)

            case "pop" | "remove":
                polyline = to_polyline(args["value"])
                layer = self._polylines[polyline.layer_id]
                layer.remove()
                del self._polylines[polyline.layer_id]

            case "clear":
                for layer_id, layer in self._polylines.items():
                    layer.remove()
                self._polylines.clear()

    def bind(
        self,
        source: Observable,
        property_name: str,
        local_name: str,
        handler: ObserverHandler | None = None,
        converter: ValueConverter | None = None,
    ) -> Self:
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
                    obs_list: ObservableList = polylines
                    obs_list.register(self._polylines_handler)
                self._polyline_converter = converter
                return self
            case "polygons":
                polygons = getattr(source, property_name)
                if isinstance(polygons, ObservableList):
                    obs_list: ObservableList = polygons
                    obs_list.register(self._polygons_handler)
                self._polygon_converter = converter
                return self

        Observer.bind(self, source, property_name, local_name, handler, converter)
        return self

    def invalidate_size(self, animate: bool = False) -> Self:
        self.run_map_method("invalidateSize", animate)
        return self

    def fit_bounds(self, bounds: List[LatLng], options: Dict | None = None) -> Self:
        if len(bounds) > 0:
            min_lat = min(b.lat for b in bounds)
            max_lat = max(b.lat for b in bounds)
            min_lng = min(b.lng for b in bounds)
            max_lng = max(b.lng for b in bounds)
            bounds_list = [[min_lat, min_lng], [max_lat, max_lng]]
            self.run_map_method("fitBounds", bounds_list, options)
        return self
