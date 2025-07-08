import asyncio
from typing import Any, Mapping

from nicegui import ui

from app.converters.map import MapPolylineValueConverter, MapPolylineGridConverter
from nicemvvm import nm
from nicemvvm.controls.LeafletMap import LatLng
from nicemvvm.observables.Observable import Observable


class MapView(ui.column):
    def __init__(self, view_model: Observable):
        super().__init__()
        view_model.register(self._listener)

        with ui.splitter(horizontal=True, value=80).classes(
            "w-full h-full"
        ) as splitter:
            with splitter.before:
                self._map = (
                    nm.leaflet()
                    .classes("h-full w-full")
                    .bind(view_model, "zoom", "zoom")
                    .bind(view_model, "center", "center")
                    .bind(
                        view_model,
                        "polylines",
                        "polylines",
                        converter=MapPolylineValueConverter(),
                    )
                )
                asyncio.create_task(self._setup_map())

            with splitter.after:
                grid = (
                    nm.gridview(
                        row_selection="multiple",
                        supress_auto_size=True,
                        supress_size_to_fit=True,
                    )
                    .classes("h_full h-full")
                    .bind(view_model, "polylines", "items",
                          converter=MapPolylineGridConverter(),)
                )
                grid.columns = [
                    nm.gridview_col(
                        header="Trip",
                        field="traj_id",
                        filter=True,
                        width=60,
                        selection=True,
                    ),
                    nm.gridview_col(
                        header="Vehicle", field="vehicle_id", filter=True, width=60
                    ),
                    nm.gridview_col(
                        header="Trace", field="trace_name", filter=True, width=60
                    ),
                    nm.gridview_col(header="km", field="km", filter=True, width=60),
                ]
                grid.row_id = "polyline_id"

            # Make sure the map is correctly resized
            splitter.on_value_change(lambda _: self._map.invalidate_size(animate=True))
            splitter.on("resize", lambda _: self._map.invalidate_size(animate=True))

    async def _setup_map(self):
        await self._map.initialized()

        self._map.fit_bounds(
            bounds=[
                LatLng(42.2203052778, -83.8042902778),
                LatLng(42.3258, -83.674),
            ]
        )

    def _listener(self, action: str, args: Mapping[str, Any]) -> None:
        match action:
            case "property":
                name = args["name"]
                value = args["value"]

                if name == "bounds":
                    self._map.fit_bounds(value)
