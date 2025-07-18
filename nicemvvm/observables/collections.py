from typing import Any, Iterable, SupportsIndex

from nicemvvm.observables.observability import Observable


class ObservableList(Observable, list):
    """A list that notifies observers when it's modified"""

    def __init__(self, data: Iterable = None):
        Observable.__init__(self)
        list.__init__(self)
        if data is not None:
            list.extend(self, data)

    def append(self, value: Any) -> None:
        list.append(self, value)
        self.notify("append", value=value, index=len(self) - 1)

    def extend(self, iterable: Iterable) -> None:
        old_length = len(self)
        list.extend(self, iterable)
        self.notify("extend", values=list(iterable), start_index=old_length)

    def insert(self, index: SupportsIndex, value: Any) -> None:
        list.insert(self, index, value)
        self.notify("insert", value=value, index=index)

    def remove(self, value: Any) -> None:
        index = self.index(value)  # Get index before removing
        list.remove(self, value)
        self.notify("remove", value=value, index=index)

    def pop(self, index: SupportsIndex = -1) -> Any:
        ix = int(index)
        actual_index = index if ix >= 0 else len(self) + ix
        item = list.pop(self, index)
        self.notify("pop", value=item, index=actual_index)
        return item

    def clear(self) -> None:
        old_items = list(self)
        list.clear(self)
        self.notify("clear", old_items=old_items)

    def __delitem__(self, key: SupportsIndex | slice) -> None:
        if isinstance(key, slice):
            old_items = self[key]
            list.__delitem__(self, key)
            self.notify("delete_slice", slice=key, removed_items=old_items)
        else:
            old_value = self[key]
            list.__delitem__(self, key)
            self.notify("delete_item", index=key, value=old_value)

    def __setitem__(self, key: SupportsIndex | slice, value: Any) -> None:
        if isinstance(key, slice):
            old_items = self[key]
            list.__setitem__(self, key, value)
            self.notify("set_slice", slice=key, old_values=old_items, new_values=value)
        else:
            old_value = self[key]
            list.__setitem__(self, key, value)
            self.notify("set_item", index=key, old_value=old_value, new_value=value)

    def __iadd__(self, other: Iterable) -> "ObservableList":
        old_length = len(self)
        list.__iadd__(self, other)
        self.notify("iadd", values=list(other), start_index=old_length)
        return self


class ObservableDict(Observable, dict):
    """A dictionary that notifies observers when it's modified"""

    def __init__(self, *args, **kwargs):
        Observable.__init__(self)
        dict.__init__(self, *args, **kwargs)

    def __setitem__(self, key: Any, value: Any) -> None:
        old_value = self.get(key, None)
        had_key = key in self
        dict.__setitem__(self, key, value)

        if had_key:
            self.notify("update", key=key, old_value=old_value, new_value=value)
        else:
            self.notify("add", key=key, value=value)

    def __delitem__(self, key: Any) -> None:
        old_value = self[key]
        dict.__delitem__(self, key)
        self.notify("delete", key=key, value=old_value)

    def clear(self) -> None:
        old_items = dict(self)
        dict.clear(self)
        self.notify("clear", old_items=old_items)

    def pop(self, key: Any, default=None) -> Any:
        if key in self:
            value = dict.pop(self, key)
            self.notify("pop", key=key, value=value)
            return value
        elif default is not None:
            return default
        else:
            raise KeyError(key)

    def update(self, other=(), /, **kwargs) -> None:
        # Capture old state
        old_dict = dict(self)
        dict.update(self, other, **kwargs)

        # Find what changed
        for key, value in self.items():
            if key not in old_dict:
                self.notify("add", key=key, value=value)
            elif old_dict[key] != value:
                self.notify("update", key=key, old_value=old_dict[key], new_value=value)
