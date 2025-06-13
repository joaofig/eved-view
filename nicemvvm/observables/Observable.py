from typing import Callable, Any, Coroutine, Dict, List, Self, Mapping, Set
from abc import ABC

ObserverHandler = Callable[[str, Mapping[str, Any]], None | Coroutine[Any, Any, None]]


class Observable(ABC):
    def __init__(self):
        self._handlers: Set[ObserverHandler] = set()

    def register(self,
                 handler: ObserverHandler):
        if handler not in self._handlers:
            self._handlers.add(handler)

    def unregister(self, handler: ObserverHandler) -> None:
        if handler in self._handlers:
            self._handlers.remove(handler)

    def notify(self, action: str, **kwargs) -> None:
        for handler in self._handlers:
            handler(action, kwargs)

    def notify_set(self,
                   name: str,
                   value: Any) -> None:
        prop_name = f"_{name}"
        old_value = getattr(self, prop_name)
        if old_value is not value or old_value != value:
            setattr(self, prop_name, value)
            self.notify("property",
                        name=name,
                        value=value)


class Observer:
    def __init__(self) -> None:
        self._prop_map: Dict[str, str] = {}
        self._prop_pam: Dict[str, str] = {}
        self._source_map: Dict[str, Observable] = {}

    def bind(self,
             source: Observable,
             property_name: str,
             local_name: str,
             handler: ObserverHandler|None = None) -> Self:
        self._prop_map[property_name] = local_name
        self._source_map[local_name] = source
        self._prop_pam[local_name] = property_name
        source.register(handler or self._inbound_handler)
        setattr(self, local_name, getattr(source, property_name))
        return self

    def unbind(self, local_name: str,
               source: Observable,
               handler: ObserverHandler|None = None) -> None:
        if local_name in self._prop_map:
            property_name = self._prop_pam[local_name]
            source.unregister(handler or self._inbound_handler)
            del self._source_map[local_name]
            del self._prop_pam[local_name]
            del self._prop_map[property_name]

    def _inbound_handler(self,
                         action: str,
                         args: Mapping[str, Any]) -> None:
        """
        This is the default binding handler that just propagates the changed value to an internal property.
        :param _: Not used.
        :param property_name: The name of the changed property.
        :param value: The changed property value.
        :return: None
        """
        if action == "property":
            property_name = args["name"]
            if property_name in self._prop_map:
                local_name = self._prop_map[property_name]

                value = args["value"]
                if value != getattr(self, local_name):
                    setattr(self, local_name, value)

    def _outbound_handler(self, local_name: str, value: Any) -> None:
        if local_name in self._prop_pam:
            property_name = self._prop_pam[local_name]
            source = self._source_map[local_name]
            setattr(source, property_name, value)
