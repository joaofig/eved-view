from typing import Callable, Any, Coroutine, Dict, List

ObserverHandler = Callable[[object, str, Any], None | Coroutine[Any, Any, None]]


class Observable:
    def __init__(self):
        self._handlers: Dict[str, List[ObserverHandler]] = {}

    def register(self, property_name: str, handler: ObserverHandler):
        if property_name not in self._handlers:
            self._handlers[property_name] = []
        self._handlers[property_name].append(handler)

    def unregister(self, property_name: str, handler: ObserverHandler) -> None:
        if property_name in self._handlers:
            prop_handlers = self._handlers[property_name]
            prop_handlers.remove(handler)

    def notify(self, property_name: str, value: Any) -> None:
        if property_name in self._handlers:
            prop_handlers = self._handlers[property_name]
            for handler in prop_handlers:
                handler(self, property_name, value)

    def notify_set(self, property_name: str, value: Any) -> None:
        prop_name = f"_{property_name}"
        old_value = getattr(self, prop_name)
        if old_value is not value or old_value != value:
            setattr(self, prop_name, value)
            self.notify(property_name, value)


class Observer:
    def __init__(self) -> None:
        self._prop_map: Dict[str, str] = {}
        self._prop_pam: Dict[str, str] = {}
        self._source_map: Dict[str, Observable] = {}

    def bind(self,
             source: Observable,
             property_name: str,
             local_name: str,
             handler: ObserverHandler|None = None) -> None:
        self._prop_map[property_name] = local_name
        self._source_map[local_name] = source
        self._prop_pam[local_name] = property_name
        source.register(property_name, handler or self._inbound_handler)
        setattr(self, local_name, getattr(source, property_name))

    def unbind(self, local_name: str,
               source: Observable,
               handler: ObserverHandler|None = None) -> None:
        if local_name in self._prop_map:
            property_name = self._prop_pam[local_name]
            source.unregister(property_name, handler or self._inbound_handler)
            del self._source_map[local_name]
            del self._prop_pam[local_name]
            del self._prop_map[property_name]

    def _inbound_handler(self, _: object, property_name: str, value: Any) -> None:
        """
        This is the default binding handler that just propagates the changed value to an internal property.
        :param _: Not used.
        :param property_name: The name of the changed property.
        :param value: The changed property value.
        :return: None
        """
        if property_name in self._prop_map:
            local_name = self._prop_map[property_name]

            if value != getattr(self, local_name):
                setattr(self, local_name, value)

    def _outbound_handler(self, local_name: str, value: Any) -> None:
        if local_name in self._prop_pam:
            property_name = self._prop_pam[local_name]
            source = self._source_map[local_name]
            setattr(source, property_name, value)
