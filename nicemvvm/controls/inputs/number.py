from typing import Optional, Self, Union

from nicegui import ui
from nicegui.elements.mixins.validation_element import (
    ValidationDict,
    ValidationFunction,
)
from nicegui.events import Handler, ValueChangeEventArguments

from nicemvvm.converter import ValueConverter
from nicemvvm.observables.observability import Observable, Observer, ObserverHandler


class NumberInput(ui.number, Observer):
    def __init__(
        self,
        label: Optional[str] = None,
        *,
        placeholder: Optional[str] = None,
        value: Optional[float] = None,
        min: Optional[float] = None,  # pylint: disable=redefined-builtin
        max: Optional[float] = None,  # pylint: disable=redefined-builtin
        precision: Optional[int] = None,
        step: Optional[float] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        format: Optional[str] = None,  # pylint: disable=redefined-builtin
        on_change: Optional[Handler[ValueChangeEventArguments]] = None,
        validation: Optional[Union[ValidationFunction, ValidationDict]] = None,
    ):
        ui.number.__init__(
            self,
            label=label,
            placeholder=placeholder,
            value=value,
            min=min,
            max=max,
            precision=precision,
            step=step,
            prefix=prefix,
            suffix=suffix,
            format=format,
            on_change=on_change,
            validation=validation,
        )

    def _value_changed_handler(self) -> None:
        self.propagate(local_name="value", value=self.value)

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
