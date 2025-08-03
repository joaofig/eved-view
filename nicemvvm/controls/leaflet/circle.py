from dataclasses import asdict

from nicegui import ui
from nicegui.elements.leaflet_layers import GenericLayer

from nicemvvm.controls.leaflet.path import Path
from nicemvvm.controls.leaflet.types import LatLng


class Circle(Path):
    def __init__(
        self,
        layer_id: str,
        center: LatLng,
        radius: float,
        stroke: bool = True,
        color: str = "#3388ff",
        opacity: float = 1.0,
        weight: float = 3.0,
        line_cap: str = "round",
        line_join: str = "round",
        dash_array: str = "",
        dash_offset: str = "",
        fill: bool = True,
        fill_color: str = "#3388ff",
        fill_opacity: float = 0.2,
        fill_rule: str = "evenodd",
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
        )
        self._center = center
        self._radius = radius
        self._options["radius"] = self._radius

    @property
    def radius(self) -> bool:
        return self._options["radius"]

    @radius.setter
    def radius(self, value: bool):
        self._options["radius"] = value
        if self._layer is not None:
            self._layer.run_method("setRadius", value)

    def add_to(self, leaflet: ui.leaflet) -> GenericLayer:
        self.remove()
        self._layer = leaflet.generic_layer(
            name="circle", args=[asdict(self._center), self._options]
        )
        self._wire_js_events("circle")
        return self._layer
