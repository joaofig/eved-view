from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Self, Union

from nicegui import ui
from nicegui.elements.leaflet_layers import GenericLayer
from nicegui.events import GenericEventArguments

from nicemvvm.observables.Observable import (
    Observable,
    Observer,
    ObserverHandler,
)
from nicemvvm.observables.ObservableCollections import ObservableList
from nicemvvm.ValueConverter import ValueConverter


@dataclass
class LatLng:
    lat: float
    lng: float
    alt: float = 0.0

    def to_list(self) -> List[float]:
        return [self.lat, self.lng]


class Path(Observer):
    def __init__(
            self,
            layer_id: str,
            stroke: bool = True,
            color: str = "#3388ff",
            opacity: float = 1.0,
            weight: float = 3.0,
            line_cap: str = "round",
            line_join: str = "round",
            dash_array: str = "",
            dash_offset: int = 0,
            fill: bool = False,
            fill_color: str = "#3388ff",
            fill_opacity: float = 0.2,
            fill_rule: str = "evenodd",
            **kwargs,
    ):
        super().__init__(**kwargs)
        self._map: ui.leaflet | None = None
        self._options = {
            "stroke": stroke,
            "color": color,
            "opacity": opacity,
            "weight": weight,
            "lineCap": line_cap,
            "lineJoin": line_join,
            "dashArray": dash_array,
            "dashOffset": dash_offset,
            "fill": fill,
            "fillColor": fill_color,
            "fillOpacity": fill_opacity,
            "fillRule": fill_rule,
        }
        self._layer: GenericLayer | None = None
        self._layer_id = layer_id

    def to_dict(self):
        return self._options

    def redraw(self):
        if self._layer is not None:
            self._layer.run_method("redraw", None)

    def set_style(self) -> None:
        if self._layer is not None:
            self._layer.run_method("setStyle", self._options)

    def remove(self):
        if self._layer is not None:
            self._layer.run_method("remove", None)

    @property
    def layer_id(self) -> str:
        return self._layer_id

    @property
    def stroke(self) -> bool:
        return self._options["stroke"]

    @stroke.setter
    def stroke(self, value: bool):
        self._options["stroke"] = value
        self.set_style()

    @property
    def color(self) -> str:
        return self._options["color"]

    @color.setter
    def color(self, value: str):
        self._options["color"] = value
        self.set_style()

    @property
    def opacity(self) -> float:
        return self._options["opacity"]

    @opacity.setter
    def opacity(self, value: float):
        self._options["opacity"] = value
        self.set_style()

    @property
    def weight(self) -> float:
        return self._options["weight"]

    @weight.setter
    def weight(self, value: float):
        self._options["weight"] = value
        self.set_style()

    @property
    def line_cap(self) -> str:
        return self._options["lineCap"]

    @line_cap.setter
    def line_cap(self, value: str):
        self._options["lineCap"] = value
        self.set_style()

    @property
    def line_join(self) -> str:
        return self._options["lineJoin"]

    @line_join.setter
    def line_join(self, value: str):
        self._options["lineJoin"] = value
        self.set_style()

    @property
    def dash_array(self) -> str:
        return self._options["dashArray"]

    @dash_array.setter
    def dash_array(self, value: str):
        self._options["dashArray"] = value
        self.set_style()

    @property
    def dash_offset(self) -> int:
        return self._options["dashOffset"]

    @dash_offset.setter
    def dash_offset(self, value: int):
        self._options["dashOffset"] = value
        self.set_style()

    @property
    def fill(self) -> bool:
        return self._options["fill"]

    @fill.setter
    def fill(self, value: bool):
        self._options["fill"] = value
        self.set_style()

    @property
    def fill_color(self) -> str:
        return self._options["fillColor"]

    @fill_color.setter
    def fill_color(self, value: str):
        self._options["fillColor"] = value
        self.set_style()

    @property
    def fill_opacity(self) -> float:
        return self._options["fillOpacity"]

    @fill_opacity.setter
    def fill_opacity(self, value: float):
        self._options["fillOpacity"] = value
        self.set_style()

    @property
    def fill_rule(self) -> str:
        return self._options["fillRule"]

    @fill_rule.setter
    def fill_rule(self, value: str):
        self._options["fillRule"] = value
        self.set_style()


class Polyline(Path):
    def __init__(
            self,
            layer_id: str,
            points: List[LatLng],
            smooth_factor: float = 1.0,
            no_clipping: bool = False,
            stroke: bool = True,
            color: str = "#3388ff",
            opacity: float = 1.0,
            weight: float = 3.0,
            line_cap: str = "round",
            line_join: str = "round",
            dash_array: str = "",
            dash_offset: int = 0,
            fill: bool = False,
            fill_color: str = "#3388ff",
            fill_opacity: float = 0.2,
            fill_rule: str = "evenodd",
            **kwargs,
    ):
        Path.__init__(
            self,
            layer_id=layer_id,
            stroke=stroke,
            color=color,
            opacity=opacity,
            weight=weight,
            line_cap=line_cap,
            line_join=line_join,
            dash_array=dash_array,
            dash_offset=dash_offset,
            fill=fill,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            fill_rule=fill_rule,
            **kwargs,
        )
        self._options["noClipping"] = no_clipping
        self._options["smoothFactor"] = smooth_factor
        self._points: List[LatLng] = points

    @property
    def smooth_factor(self) -> float:
        return self._options["smoothFactor"]

    @smooth_factor.setter
    def smooth_factor(self, value: float):
        self._options["smoothFactor"] = value
        self.set_style()

    @property
    def no_clipping(self) -> bool:
        return self._options["noClipping"]

    @no_clipping.setter
    def no_clipping(self, value: bool):
        self._options["noClipping"] = value
        self.set_style()

    @property
    def points(self) -> List[LatLng]:
        return self._points

    @points.setter
    def points(self, points: List[LatLng]):
        self._points = points
        if self._layer is not None:
            self._layer.run_method("setLatLngs", self._points)

    @property
    async def center(self) -> LatLng | None:
        if self._layer is not None:
            center = await self._layer.run_method("getCenter", None)
            return LatLng(center.lat, center.lng)
        return None

    @property
    async def bounds(self) -> List[LatLng]:
        if self._layer is not None:
            bounds = await self._layer.run_method("getBounds", None)
            return [LatLng(b.lat, b.lng) for b in bounds]
        else:
            return self._points

    def add_to(self, leaflet: ui.leaflet) -> GenericLayer:
        self.remove()
        self._layer = leaflet.generic_layer(
            name="polyline", args=[self._points, self._options]
        )
        return self._layer


class Polygon(Polyline):
    def __init__(
            self,
            layer_id: str,
            points: List[LatLng],
            smooth_factor: float = 1.0,
            no_clipping: bool = False,
            stroke: bool = True,
            color: str = "#3388ff",
            opacity: float = 1.0,
            weight: float = 3.0,
            line_cap: str = "round",
            line_join: str = "round",
            dash_array: str = "",
            dash_offset: int = 0,
            fill: bool = True,
            fill_color: str = "#3388ff",
            fill_opacity: float = 0.2,
            fill_rule: str = "evenodd",
            **kwargs,
    ):
        Polyline.__init__(
            self,
            layer_id=layer_id,
            points=points,
            smooth_factor=smooth_factor,
            no_clipping=no_clipping,
            stroke=stroke,
            color=color,
            opacity=opacity,
            weight=weight,
            line_cap=line_cap,
            line_join=line_join,
            dash_array=dash_array,
            dash_offset=dash_offset,
            fill=fill,
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            fill_rule=fill_rule,
            **kwargs,
        )

    def add_to(self, leaflet: ui.leaflet) -> GenericLayer:
        self.remove()
        self._layer = leaflet.generic_layer(
            name="polygon", args=[self._points, self._options]
        )
        return self._layer


class ControlPosition(Enum):
    TOPLEFT = "topleft"
    TOPRIGHT = "topright"
    BOTTOMLEFT = "bottomleft"
    BOTTOMRIGHT = "bottomright"


@dataclass
class DrawControl:
    position: ControlPosition = ControlPosition.TOPLEFT


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
