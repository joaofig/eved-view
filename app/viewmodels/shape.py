from nicemvvm.observables.observability import Observable, notify_change


class MapShape(Observable):
    def __init__(
        self,
        shape_id: str,
        color: str,
        weight: float,
        opacity: float,
        fill: bool,
        fill_color: str,
        fill_opacity: float,
        dash_array: str = "",
        dash_offset: str = "",
    ):
        super().__init__()
        self._shape_id = shape_id
        self._color = color
        self._weight = weight
        self._opacity = opacity
        self._dash_array = dash_array
        self._dash_offset = dash_offset
        self._fill = fill
        self._fill_color = fill_color
        self._fill_opacity = fill_opacity

    @property
    def shape_id(self) -> str:
        return self._shape_id

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    @notify_change
    def color(self, value: str):
        self._color = value

    @property
    def weight(self) -> float:
        return self._weight

    @weight.setter
    @notify_change
    def weight(self, value: float):
        self._weight = value

    @property
    def opacity(self) -> float:
        return self._opacity

    @opacity.setter
    @notify_change
    def opacity(self, value: float):
        self._opacity = value

    @property
    def fill(self) -> bool:
        return self._fill

    @fill.setter
    @notify_change
    def fill(self, value: bool):
        self._fill = value

    @property
    def fill_color(self) -> str:
        return self._fill_color

    @fill_color.setter
    @notify_change
    def fill_color(self, value: str):
        self._fill_color = value

    @property
    def fill_opacity(self) -> float:
        return self._fill_opacity

    @fill_opacity.setter
    @notify_change
    def fill_opacity(self, value: float):
        self._fill_opacity = value

    @property
    def dash_array(self) -> str:
        return self._dash_array

    @dash_array.setter
    @notify_change
    def dash_array(self, value: str):
        self._dash_array = value

    @property
    def dash_offset(self) -> str:
        return self._dash_offset

    @dash_offset.setter
    @notify_change
    def dash_offset(self, value: str):
        self._dash_offset = value
