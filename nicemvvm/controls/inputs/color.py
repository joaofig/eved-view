from typing import Optional, Self

from nicegui import ui
from nicegui.events import Handler, ValueChangeEventArguments

from nicemvvm.converter import ValueConverter
from nicemvvm.observables.observability import Observable, Observer, ObserverHandler


class ColorInput(ui.color_input, Observer):
    def __init__(
        self,
        label: Optional[str] = None,
        *,
        placeholder: Optional[str] = None,
        value: str = "",
        on_change: Optional[Handler[ValueChangeEventArguments]] = None,
        preview: bool = False,
    ):
        super().__init__(
            label,
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            preview=preview,
        )

    def _value_changed_handler(self) -> None:
        self._outbound_handler(local_name="value", value=self.value)

    def bind(
        self,
        source: Observable,
        property_name: str,
        local_name: str,
        handler: ObserverHandler | None = None,
        converter: ValueConverter | None = None,
    ) -> Self:
        if local_name == "value":
            self.on_value_change(self._value_changed_handler)
        return Observer.bind(
            self, source, property_name, local_name, handler, converter
        )
