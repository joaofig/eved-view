from nicegui import ui
from nicegui.elements.leaflet_layers import GenericLayer

from nicemvvm.observables.Observable import Observer


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
