from nicegui import ui

from app.viewmodels.map import RemoveRouteCommand
from nicemvvm.controls.button import Button
from nicemvvm.controls.inputs.color import ColorInput
from nicemvvm.controls.inputs.number import NumberInput
from nicemvvm.observables.observability import Observable, notify_change, Observer


class PolygonPropertyView(ui.column, Observer, Observable):
    def __init__(self, view_model: Observable | None = None, **kwargs):
        super().__init__(**kwargs)
        self._observable: Observable | None = None
        self._remove_command: RemoveRouteCommand | None = None

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

                    self._fill_opacity_input = NumberInput(
                        label="Fill Opacity",
                        value=0.2,
                        min=0.0,
                        max=1.0,
                        step=0.1,
                        precision=2,
                    ).classes("w-full edit-view-field")

                    self._fill_color_input = ColorInput(
                        label="Fill Color", value="#3388ff", preview=True
                    ).classes("w-full edit-view-field")

        # Store input objects in a collection for easy iteration
        self._input_controls = [
            self._weight_input,
            self._opacity_input,
            self._color_input,
            self._fill_opacity_input,
            self._fill_color_input,
            self._remove_button
        ]

        # Disable all controls initially
        for control in self._input_controls:
            control.disable()

        self.bind(view_model, "selected_polyline", "observable")
        self.bind(view_model, "remove_route_command", "remove_command")

    def _enable_all_controls(self):
        """Enable all input controls."""
        for control in self._input_controls:
            control.enable()

    def _disable_all_controls(self):
        """Disable all input controls."""
        for control in self._input_controls:
            control.disable()

    @property
    def observable(self) -> Observable | None:
        return self._observable

    @observable.setter
    @notify_change
    def observable(self, observable: Observable | None):
        if observable is None:
            if self._observable is not None:
                self._weight_input.unbind("weight", self._observable)
                self._opacity_input.unbind("opacity", self._observable)
                self._color_input.unbind("color", self._observable)

                self._fill_opacity_input.unbind("fill_opacity", self._observable)
                self._fill_color_input.unbind("fill_color", self._observable)
            self._disable_all_controls()

        self._observable = observable
        if observable is not None:
            self._weight_input.bind(observable, "weight", "value")
            self._opacity_input.bind(observable, "opacity", "value")
            self._color_input.bind(observable, "color", "value")

            self._fill_opacity_input.bind(observable, "fill_opacity", "value")
            self._fill_color_input.bind(observable, "fill_color", "value")

            self._enable_all_controls()

    @property
    def remove_command(self) -> RemoveRouteCommand | None:
        return self._remove_command

    @remove_command.setter
    @notify_change
    def remove_command(self, remove_command: RemoveRouteCommand | None):
        self._remove_command = remove_command
        self._remove_button.command = remove_command
