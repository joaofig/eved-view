from typing import Any, Callable

from nicemvvm.observables.observability import Observable, Observer, notify_change


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

    def execute(self, arg: Any = None) -> Any:
        return None

    async def async_execute(self, arg: Any = None) -> Any:
        return None


class RelayCommand(Command, Observer):
    def __init__(
        self,
        action: Callable[[Any], Any],
        is_enabled: bool = True,
        **kwargs,
    ):
        super().__init__(is_enabled=is_enabled, **kwargs)
        self._action = action

    def execute(self, arg: Any = None) -> Any:
        return self._action(arg)
