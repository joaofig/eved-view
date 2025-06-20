from nicemvvm.observables.Observable import Observable, notify
from typing import Any


class Command(Observable):
    def __init__(self, is_async: bool = False):
        super().__init__()
        self._is_enabled: bool = True
        self._is_async: bool = is_async

    @property
    def is_enabled(self) -> bool:
        return self._is_enabled

    @is_enabled.setter
    @notify
    def is_enabled(self, value: bool):
        self._is_enabled = value

    @property
    def is_async(self) -> bool:
        return self._is_async

    def run(self, arg: Any = None) -> Any:
        return None

    async def run_async(self, arg: Any = None) -> Any:
        return None
