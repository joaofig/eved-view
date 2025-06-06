from typing import Dict, List

from nicemvvm.Observable import Observable


class MapViewModel(Observable):
    def __init__(self):
        super().__init__()
        self._zoom = 10
        self._center: List[float] = [0.0, 0.0]
        self._center_text: str = "(0, 0)"

    @property
    def zoom(self) -> int:
        return self._zoom

    @zoom.setter
    def zoom(self, value: int) -> None:
        self.notify_set("zoom", value)

    @property
    def center(self) -> List[float]:
        return self._center

    @center.setter
    def center(self, value: List[float]) -> None:
        self.notify_set("center", value)
        self.center_text = f"({self.center[0]}, {self.center[1]})"

    @property
    def center_text(self) -> str:
        return self._center_text

    @center_text.setter
    def center_text(self, text: str) -> None:
        self.notify_set("center_text", text)
