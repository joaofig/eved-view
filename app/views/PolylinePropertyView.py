from nicegui import ui

from nicemvvm.observables.Observable import Observer, Observable


class PolylinePropertyView(ui.column, Observer):
    def __init__(self, view_model: Observable):
        super().__init__()

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
                # ui.button("Apply", on_click=lambda _: print("clicked"))
                ui.button("Remove").classes("w-full m-0").props("icon=delete")

            with ui.row().classes("w-full h-full gap-0"):
                with ui.scroll_area() \
                        .classes("w-full h-full custom-scroll-area"):
                    ui.number(label="Weight", value=3.0).classes("w-full edit-view-field")
                    ui.number(label="Opacity", value=0.6).classes("w-full edit-view-field")
