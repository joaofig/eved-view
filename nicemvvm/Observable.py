from typing import Callable, Any, Coroutine

Observer = Callable[[object, str, Any], None | Coroutine[Any, Any, None]]


class Observable:
    def __init__(self):
        self._observers = list()

    def bind(self, observer: Observer) -> None:
        self.unbind(observer)
        if observer not in self._observers:
            self._observers.append(observer)

    def unbind(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, property_name: str, value: Any) -> None:
        for observer in self._observers:
            observer(self, property_name, value)

    def notify_set(self, property_name: str, value: Any) -> None:
        prop_name = f"_{property_name}"
        old_value = getattr(self, prop_name)
        if old_value is not value or old_value != value:
            setattr(self, prop_name, value)
            self.notify(property_name, value)
