from typing import Any, Dict, List, Self, Union, Mapping

from nicegui import ui
from nicegui.events import GenericEventArguments

from nicemvvm.command import Command
from nicemvvm.controls.leaflet.circle import Circle
from nicemvvm.controls.leaflet.path import Path
from nicemvvm.controls.leaflet.polygon import Polygon
from nicemvvm.controls.leaflet.polyline import Polyline
from nicemvvm.controls.leaflet.types import LatLng, GeoBounds
from nicemvvm.converter import ValueConverter
from nicemvvm.observables.collections import ObservableList
from nicemvvm.observables.observability import Observable, Observer, ObserverHandler


class LeafletMap(ui.leaflet, Observer):
    def __init__(
        self,
        draw_control: Union[bool, Dict] = False,
        hide_drawn_items: bool = False,
        options=None,
        **kwargs,
    ):
        if not options:
            options = dict()

        ui.leaflet.__init__(
            self, draw_control=draw_control,
            hide_drawn_items=hide_drawn_items,
            options=options,
            **kwargs,
        )
        Observer.__init__(self)

        if options is None:
            options = {}
        self._polylines: Dict[str, Polyline] = {}
        self._polyline_converter: ValueConverter | None = None
        self._polygons: Dict[str, Polygon] = {}
        self._polygon_converter: ValueConverter | None = None
        self._circles: Dict[str, Circle] = {}
        self._circle_converter: ValueConverter | None = None

        self.click_command: Command | None = None
        self.polyline_click_command: Command | None = None
        self.polyline_dblclick_command: Command | None = None
        self.polyline_contextmenu_command: Command | None = None
        self.polygon_click_command: Command | None = None
        self.polygon_dblclick_command: Command | None = None
        self.polygon_contextmenu_command: Command | None = None
        self.circle_click_command: Command | None = None
        self.circle_dblclick_command: Command | None = None
        self.circle_contextmenu_command: Command | None = None
        self.double_click_command: Command | None = None
        self.contextmenu_command: Command | None = None

    def _on_click(self, e: GenericEventArguments):
        if self.click_command is not None:
            latlng = e.args["latlng"]
            point = LatLng(latlng["lat"], latlng["lng"])
            self.click_command.execute(point)

    def _on_double_click(self, e: GenericEventArguments):
        if self.double_click_command is not None:
            latlng = e.args["latlng"]
            point = LatLng(latlng["lat"], latlng["lng"])
            self.double_click_command.execute(point)

    def _on_polyline_click(self, e: GenericEventArguments):
        if self.polyline_click_command:
            self.polyline_click_command.execute(e.args["layerId"])

    def _on_polyline_dblclick(self, e: GenericEventArguments):
        if self.polyline_dblclick_command:
            self.polyline_dblclick_command.execute(e.args["layerId"])

    def _on_polyline_contextmenu(self, e: GenericEventArguments):
        if self.polyline_contextmenu_command:
            self.polyline_contextmenu_command.execute(e.args["layerId"])

    def _on_polygon_click(self, e: GenericEventArguments):
        if self.polygon_click_command:
            self.polygon_click_command.execute(e.args["layerId"])

    def _on_polygon_dblclick(self, e: GenericEventArguments):
        if self.polygon_dblclick_command:
            self.polygon_dblclick_command.execute(e.args["layerId"])

    def _on_polygon_contextmenu(self, e: GenericEventArguments):
        if self.polygon_contextmenu_command:
            self.polygon_contextmenu_command.execute(e.args["layerId"])

    def _on_circle_click(self, e: GenericEventArguments):
        if self.circle_click_command:
            self.circle_click_command.execute(e.args["layerId"])

    def _on_circle_dblclick(self, e: GenericEventArguments):
        if self.circle_dblclick_command:
            self.circle_dblclick_command.execute(e.args["layerId"])

    def _on_circle_contextmenu(self, e: GenericEventArguments):
        if self.circle_contextmenu_command:
            self.circle_contextmenu_command.execute(e.args["layerId"])

    def _on_map_move(self, e: GenericEventArguments):
        center = e.args["center"]
        self.propagate("center", center)

    def _on_map_zoom(self, e: GenericEventArguments):
        zoom = e.args["zoom"]
        self.propagate("zoom", zoom)

    def _shape_handler(
        self,
        action: str,
        args: Mapping[str, Any],
        shapes: Dict[str, Path],
        converter: ValueConverter,
    ) -> None:
        def to_path(v: Any) -> Path | None:
            return None if not v or not converter else converter.convert(v)

        def add_path(v: Any) -> None:
            p: Path = to_path(v)
            if p and p.layer_id not in shapes:
                p.add_to(self)
                shapes[p.layer_id] = p

        match action:
            case "append":
                add_path(args["value"])

            case "extend":
                for value in args["values"]:
                    add_path(value)

            case "pop" | "remove":
                polygon = to_path(args["value"])
                layer = shapes[polygon.layer_id]
                layer.remove()
                del shapes[layer.layer_id]

            case "clear":
                for layer_id, layer in shapes.items():
                    layer.remove()
                shapes.clear()

    def _circles_handler(self, action: str, args: Mapping[str, Any]) -> None:
        self._shape_handler(action, args, self._circles, self._circle_converter)

    def _polygons_handler(self, action: str, args: Mapping[str, Any]) -> None:
        self._shape_handler(action, args, self._polygons, self._polygon_converter)

    def _polylines_handler(self, action: str, args: Mapping[str, Any]) -> None:
        self._shape_handler(action, args, self._polylines, self._polyline_converter)

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
            case "circles":
                circles = getattr(source, property_name)
                if isinstance(circles, ObservableList):
                    obs_list: ObservableList = circles
                    obs_list.register(self._circles_handler)
                self._circle_converter = converter
                return self

            case "click_command":
                self.on("map-click", self._on_click)
                handler = self._inbound_handler

            case "double_click_command":
                self.on("map-dblclick", self._on_double_click)
                handler = self._inbound_handler

            case "polyline_click_command":
                ui.on("polyline-click", self._on_polyline_click)
                handler = self._inbound_handler

            case "polyline_double_click_command":
                ui.on("polyline-dblclick", self._on_polyline_dblclick)
                handler = self._inbound_handler

            case "polyline_contextmenu_command":
                ui.on("polyline-contextmenu", self._on_polyline_contextmenu)
                handler = self._inbound_handler

            case "polygon_click_command":
                ui.on("polygon-click", self._on_polygon_click)
                handler = self._inbound_handler

            case "polygon_double_click_command":
                ui.on("polygon-dblclick", self._on_polygon_dblclick)
                handler = self._inbound_handler

            case "polygon_contextmenu_command":
                ui.on("polygon-contextmenu", self._on_polygon_contextmenu)
                handler = self._inbound_handler

            case "circle_click_command":
                ui.on("circle-click", self._on_circle_click)
                handler = self._inbound_handler

            case "circle_double_click_command":
                ui.on("circle-dblclick", self._on_circle_dblclick)
                handler = self._inbound_handler

            case "circle_contextmenu_command":
                ui.on("circle-contextmenu", self._on_circle_contextmenu)
                handler = self._inbound_handler

        Observer.bind(self, source, property_name, local_name, handler, converter)
        return self

    def invalidate_size(self, animate: bool = False) -> Self:
        self.run_map_method("invalidateSize", animate)
        return self

    def fit_bounds(self, bounds: GeoBounds, options: Dict | None = None) -> Self:
        bounds_list = [[bounds.sw.lat, bounds.sw.lng],
                       [bounds.ne.lat, bounds.ne.lng]]
        self.run_map_method("fitBounds", bounds_list, options)
        return self

    def zoom_in(self) -> Self:
        self.run_map_method("zoomIn")
        return self

    def zoom_out(self) -> Self:
        self.run_map_method("zoomOut")
        return self

