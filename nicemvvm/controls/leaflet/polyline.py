from typing import List

from nicegui import ui
from nicegui.elements.leaflet_layers import GenericLayer

from nicemvvm.controls.leaflet.path import Path
from nicemvvm.controls.leaflet.types import LatLng


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
