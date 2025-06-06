from typing import Callable, Any, Coroutine

ObserverHandler = Callable[[object, str, Any], None | Coroutine[Any, Any, None]]


class Observable:
    def __init__(self):
        self._handlers = list()

    def bind(self, handler: ObserverHandler) -> None:
        self.unbind(handler)
        if handler not in self._handlers:
            self._handlers.append(handler)

    def unbind(self, handler: ObserverHandler) -> None:
        if handler in self._handlers:
            self._handlers.remove(handler)

    def notify(self, property_name: str, value: Any) -> None:
        for observer in self._handlers:
            observer(self, property_name, value)

    def notify_set(self, property_name: str, value: Any) -> None:
        prop_name = f"_{property_name}"
        old_value = getattr(self, prop_name)
        if old_value is not value or old_value != value:
            setattr(self, prop_name, value)
            self.notify(property_name, value)


class ObserverMixin:
    def __init__(self, observable: Observable) -> None:
        self._observable = observable
        observable.bind(self._handler)

        self._map = dict()

    def bind(self, local_property: str, remote_property: str) -> None:
        self._map[remote_property] = local_property

    def unbind(self, remote_property: str) -> None:
        if remote_property in self._map:
            self._map.pop(remote_property, None)

    def _handler(self, _: object, property_name: str, value: Any) -> None:
        if property_name in self._map:
            local_property = self._map[property_name]
            if getattr(self, local_property) != value:
                setattr(self, local_property, value)


class CompositeObserver:
    def __init__(self,
                 observable: Observable,
                 target: object) -> None:
        self._observable = observable
        self._target = target
        observable.bind(self._handler)

        self._map = dict()

    def bind(self, target_property: str, remote_property: str) -> None:
        self._map[remote_property] = target_property

    def unbind(self, remote_property: str) -> None:
        if remote_property in self._map:
            self._map.pop(remote_property, None)

    def _handler(self, _: object, property_name: str, value: Any) -> None:
        if property_name in self._map:
            target_property = self._map[property_name]
            if getattr(self._target, target_property) != value:
                setattr(self._target, target_property, value)
