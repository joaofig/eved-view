from typing import Any

from nicemvvm.observables.Observable import Observable, notify_change


class Command(Observable):
    def __init__(self, is_async: bool = False, is_enabled: bool = True, **kwargs):
        self._is_enabled: bool = is_enabled
        self._is_async: bool = is_async
        super().__init__(**kwargs)

    @property
    def is_enabled(self) -> bool:
        return self._is_enabled

    @is_enabled.setter
    @notify_change
    def is_enabled(self, value: bool):
        self._is_enabled = value

    @property
    def is_async(self) -> bool:
        return self._is_async

    def run(self, arg: Any = None) -> Any:
        return None

    async def run_async(self, arg: Any = None) -> Any:
        return None
