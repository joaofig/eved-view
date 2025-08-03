from typing import List

from nicegui import ui
from nicegui.elements.leaflet_layers import GenericLayer

from nicemvvm.controls.leaflet.polyline import Polyline
from nicemvvm.controls.leaflet.types import LatLng


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
        dash_offset: str = "",
        fill: bool = True,
        fill_color: str = "#3388ff",
        fill_opacity: float = 0.2,
        fill_rule: str = "evenodd",
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
        )

    def add_to(self, leaflet: ui.leaflet) -> GenericLayer:
        self.remove()
        self._layer = leaflet.generic_layer(
            name="polygon", args=[self._points, self._options]
        )
        self._wire_js_events("polygon")
        return self._layer
