from nicegui import ui

from nicemvvm.controls.button import Button
from nicemvvm.controls.inputs.color import ColorInput
from nicemvvm.controls.inputs.number import NumberInput
from nicemvvm.controls.inputs.switch import SwitchInput
from nicemvvm.observables.observability import Observable, Observer


class CirclePropertyEditor(ui.column, Observer):
    def __init__(self, view_model: Observable | None = None):
        super().__init__()
        self._view_model = view_model

        with self.classes("gap-0"):
            with ui.row().classes("w-full p-0 m-0"):
                self._remove_button = (
                    Button(text="Remove").classes("w-full m-0").props("icon=delete")
                )

            with ui.row().classes("w-full h-full gap-0"):
                with ui.scroll_area().classes("w-full h-full custom-scroll-area"):
                    self._weight_input = NumberInput(
                        label="Weight",
                        value=3.0,
                        min=0.1,
                        max=10,
                        step=0.1,
                        precision=1,
                    ).classes("w-full edit-view-field")

                    self._opacity_input = NumberInput(
                        label="Opacity",
                        value=0.6,
                        min=0.0,
                        max=1.0,
                        step=0.1,
                        precision=2,
                    ).classes("w-full edit-view-field")

                    self._color_input = ColorInput(
                        label="Color", value="#3388ff", preview=True
                    ).classes("w-full edit-view-field")

                    self._fill_input = SwitchInput(text="Fill", value=True).classes(
                        "w-full edit-view-field"
                    )

                    self._fill_opacity_input = NumberInput(
                        label="Fill Opacity",
                        value=0.0,
                        min=0.0,
                        max=1.0,
                        step=0.1,
                        precision=2,
                    ).classes("w-full edit-view-field")

                    self._fill_color_input = ColorInput(
                        label="Fill Color", value="#ffffff", preview=True
                    ).classes("w-full edit-view-field")
