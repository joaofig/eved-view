from typing import Any

from nicemvvm.converter import ValueConverter


class NotNoneValueConverter(ValueConverter):
    def __init__(self):
        super().__init__()

    def convert(self, x: Any) -> Any:
        return x is not None


class IsNoneValueConverter(ValueConverter):
    def __init__(self):
        super().__init__()

    def convert(self, x: Any) -> Any:
        return x is None
