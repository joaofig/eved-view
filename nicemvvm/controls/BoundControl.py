from collections.abc import Callable
from dataclasses import dataclass
from typing import Dict, Any

from nicemvvm.Observable import ObserverHandler, Observable


@dataclass
class PropertyBind:
    local_name: str
    prop_name: str
    handler: ObserverHandler|None = None
    data_source: object|None = None


class BoundControl:
    def __init__(self):
        self.data_source: Observable|None = None
        self._handlers: Dict[str, Callable[[Any], None]] = {}
        self._prop_map: Dict[str, Callable[[Any], None]] = {}

    def _bind_dispatcher(self, source: object, name: str, value: Any) -> None:
        if name in self._handlers:
            self._handlers[name](value)

    def add_handler(self, local_name: str, handler: Callable[[Any], None]) -> None:
        self._handlers[local_name] = handler

    def bind(self, local_name: str, prop_name: str, source: Observable|None=None) -> None:
        if local_name in self._handlers:
            self._prop_map[prop_name] = self._handlers[local_name]

            if source is not None:
                source.bind(self._bind_dispatcher)
            elif self.data_source is not None:
                self.data_source.bind(self._bind_dispatcher)
