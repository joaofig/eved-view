from typing import Iterable, Any, SupportsIndex, Callable, List, Set
from inspect import iscoroutinefunction
from asyncio import run


class BaseObservable:
    def __init__(self):
        self._observers: List[Callable] = []
        self._recursion: Set[Callable] = set()

    def unsubscribe(self, observer: Callable) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def subscribe(self, observer: Callable) -> None:
        self.unsubscribe(observer)
        if observer not in self._observers:
            self._observers.append(observer)

    def notify_observers(self, *args, **kwargs) -> None:
        if kwargs is not None:
            kwargs["source"] = self
        else:
            kwargs = {"source": self}

        for observer in self._observers:
            if observer in self._recursion:
                continue

            self._recursion.add(observer)
            if iscoroutinefunction(observer):
                run(observer(*args, **kwargs))
            else:
                observer(*args, **kwargs)
            self._recursion.remove(observer)


class ObservableList(BaseObservable, list):
    def __init__(self, data: Iterable | None = None):
        super().__init__()
        if data is not None:
            super().extend(data)

    def append(self, value: Any) -> None:
        super().append(value)
        self.notify_observers(action="append", value=value)

    def extend(self, iterable: Iterable) -> None:
        super().extend(iterable)
        self.notify_observers(action="extend", value=iterable)

    def insert(self, index: SupportsIndex, value: Any) -> None:
        super().insert(index, value)
        self.notify_observers(action="insert", value=value)

    def remove(self, value: Any) -> None:
        super().remove(value)
        self.notify_observers(action="remove", value=value)

    def pop(self, index: SupportsIndex = -1) -> Any:
        item = super().pop(index)
        self.notify_observers(action="pop", value=item)
        return item

    def clear(self) -> None:
        super().clear()
        self.notify_observers(action="clear", value=None)

    def __delitem__(self, key: SupportsIndex | slice) -> None:
        super().__delitem__(key)
        self.notify_observers(action="__delitem__", value=key)

    def __setitem__(self, key: SupportsIndex | slice, value: Any) -> None:
        super().__setitem__(key, value)
        self.notify_observers(action="__setitem__", value=(key, value))

    def __add__(self, other: list) -> "ObservableList":
        super().__add__(other)
        self.notify_observers(action="__add__", value=other)
        return self

    def __iadd__(self, other: Iterable) -> "ObservableList":
        super().__iadd__(other)
        self.notify_observers(action="__iadd__", value=other)
        return self
