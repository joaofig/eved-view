import asyncio
from typing import Any, Mapping

from nicegui import ui
from nicemvvm import nm
from nicemvvm.observables.Observable import Observable


class MapView(ui.column):
    def __init__(self, view_model: Observable):
        super().__init__()
        view_model.register(self._listener)

        with ui.splitter(horizontal=True, value=80).classes("w-full h-full") as splitter:
            with splitter.before:
                self.m = (nm.leaflet()
                            .classes("h-full w-full")
                            .bind(view_model, "zoom", "zoom")
                            .bind(view_model, "center", "center")
                            .bind(view_model, "polylines", "polylines")
                          )

            with splitter.after:
                grid = nm.gridview().classes("h_full h-full") \
                    .bind_all(view_model, items="polylines")
                grid.columns = [
                    nm.gridview_col(header="Trip", field="traj_id", filter=True, width=100),
                    nm.gridview_col(header="Vehicle", field="vehicle_id", filter=True, width=100),
                    nm.gridview_col(header="Trace", field="trace_name", filter=True, width=100),
                    nm.gridview_col(header="km", field="km", filter=True, width=100),
                ]
                grid.row_id = "traj_id"

            # Make sure the map is correctly resized
            splitter.on_value_change(lambda _: self.m.invalidate_size(animate=True))
            splitter.on("resize", lambda _: self.m.invalidate_size(animate=True))

    def _listener(self, action: str, args: Mapping[str, Any]) -> None:
        match action:
            case "property":
                name = args["name"]
                value = args["value"]

                if name == "bounds":
                    self.m.fit_bounds(value)
