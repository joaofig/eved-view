from typing import Any


class ValueConverter:
    def __init__(self, context: Any = None, **kwargs: Any):
        self._context = context

    def convert(self, value: Any) -> Any:
        return value

    def reverse_convert(self, value: Any) -> Any:
        return value
