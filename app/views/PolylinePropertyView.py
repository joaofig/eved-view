from nicegui import ui

from nicemvvm.controls.ColorInput import ColorInput
from nicemvvm.controls.NumberInput import NumberInput
from nicemvvm.observables.Observable import Observable, Observer, notify_change


class PolylinePropertyView(ui.column, Observer):
    def __init__(self, view_model: Observable):
        super().__init__()
        self._observable: Observable | None = None

        ui.add_css("""
        .custom-scroll-area .q-scrollarea__content {
            padding: 0px 12px 0px 4px !important;
            gap: 0px !important;
        }
        .edit-view-field .q-field {
            padding-top: 4px !important;
        """)

        with self.classes("gap-0"):
            with ui.row().classes("w-full p-0 m-0"):
                self._remove_button = ui.button("Remove").classes("w-full m-0").props("icon=delete")

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

        self._weight_input.disable()
        self._opacity_input.disable()
        self._color_input.disable()
        self._remove_button.disable()

        self.bind(view_model, "selected_polyline", "observable", converter=None)

    @property
    def observable(self) -> Observable | None:
        return self._observable

    @observable.setter
    @notify_change
    def observable(self, observable: Observable | None):
        if observable is None and self._observable is not None:
            self._weight_input.unbind("weight", self._observable)
            self._opacity_input.unbind("opacity", self._observable)
            self._color_input.unbind("color", self._observable)

            self._weight_input.disable()
            self._opacity_input.disable()
            self._color_input.disable()
            self._remove_button.disable()

        self._observable = observable
        if observable is not None:
            self._weight_input.bind(observable, "weight", "value")
            self._opacity_input.bind(observable, "opacity", "value")
            self._color_input.bind(observable, "color", "value")

            self._weight_input.enable()
            self._opacity_input.enable()
            self._color_input.enable()
            self._remove_button.enable()
