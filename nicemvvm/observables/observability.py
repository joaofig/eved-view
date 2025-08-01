import functools
from abc import ABC
from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Dict, Mapping, Self, Set

from nicemvvm.converter import ValueConverter

ObserverHandler = Callable[[str, Mapping[str, Any]], None] | Coroutine[Any, Any, None]
ConverterFunction = Callable[[Any], Any]


def notify_change(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        name = func.__name__
        this, value = args
        old_value = getattr(this, name)
        if old_value != value and isinstance(this, Observable):
            observable: Observable = this
            observable.notify(
                action="property_changing",
                name=name,
                new_value=value,
                old_value=old_value,
            )
            ret = func(*args, **kwargs)
            observable.notify(action="property_changed", name=name, value=value)
            return ret
        return None

    return wrapper


class Observable:
    def __init__(self, **kwargs):
        self._handlers: Set[ObserverHandler] = set()
        super().__init__(**kwargs)

    def register(self, handler: ObserverHandler):
        if handler not in self._handlers:
            self._handlers.add(handler)

    def unregister(self, handler: ObserverHandler) -> None:
        if handler in self._handlers:
            self._handlers.remove(handler)

    def notify(self, action: str, **kwargs) -> None:
        for handler in self._handlers:
            handler(action, kwargs)

    def notify_set(self, name: str, value: Any) -> None:
        prop_name = f"_{name}"
        old_value = getattr(self, prop_name)
        if old_value is not value or old_value != value:
            setattr(self, prop_name, value)
            self.notify("property_changed", name=name, value=value)


@dataclass
class Binder:
    source: Observable
    property_name: str
    local_name: str
    handler: ObserverHandler | None = None
    converter: ValueConverter | None = None



class Observer:
    def __init__(self, **kwargs) -> None:
        self._prop_map: Dict[str, str] = {}
        self._conv_map: Dict[str, ValueConverter] = {}
        self._prop_pam: Dict[str, str] = {}
        self._source_map: Dict[str, Observable] = {}
        super().__init__(**kwargs)

    def bind(
        self,
        source: Observable,
        property_name: str,
        local_name: str,
        handler: ObserverHandler | None = None,
        converter: ValueConverter | None = None,
    ) -> Self:
        """
        Binds a property of an observable to a local property of this observable.
        :param source: Observable source
        :param property_name: Property name to observe
        :param local_name: Property name to bind to.
        :param handler: Optional handler to call when the property changes.
        :param converter: Optional converter function to call before setting the local property.
        :return: Returns the observer object.
        """
        self._prop_map[property_name] = local_name
        self._conv_map[property_name] = converter
        self._source_map[local_name] = source
        self._prop_pam[local_name] = property_name
        source.register(handler or self._inbound_handler)

        value = getattr(source, property_name)
        converter = self._conv_map[property_name]
        if converter is not None:
            value = converter.convert(value)
        setattr(self, local_name, value)
        return self

    def unbind(
        self,
        property_name: str,
        source: Observable,
        handler: ObserverHandler | None = None,
    ) -> None:
        if property_name in self._prop_map:
            local_name = self._prop_map[property_name]
            source.unregister(handler or self._inbound_handler)
            del self._source_map[local_name]
            del self._prop_pam[local_name]
            del self._prop_map[property_name]
            del self._conv_map[property_name]

    def _inbound_handler(self, action: str, args: Mapping[str, Any]) -> None:
        """
        This is the default binding handler that just propagates the changed value to an internal property,
        as per the bind call. The handler is called by the Observable object to which this Observer binds to.
        :param action: Action to perform.
        :param args: The arguments to pass to the action.
        :return: None
        """
        if action == "property_changed":
            property_name = args["name"]
            if property_name in self._prop_map:
                local_name = self._prop_map[property_name]

                value = args["value"]
                converter = self._conv_map[property_name]
                if converter:
                    value = converter.convert(value)
                if value != getattr(self, local_name):
                    setattr(self, local_name, value)

    def propagate(self, local_name: str, value: Any) -> None:
        """
        For properties whose values originate in the Observer, like in the case of a UI control,
        by calling this function the Observer propagates the value to the Observable.
        :param local_name: Local property name
        :param value: Local property value
        :return: None
        """
        if local_name in self._prop_pam:
            property_name = self._prop_pam[local_name]
            converter = self._conv_map[property_name]
            if converter:
                value = converter.reverse_convert(value)
            source = self._source_map[local_name]
            setattr(source, property_name, value)
