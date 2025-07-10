import asyncio
from typing import Any, Mapping

from nicegui import ui

from app.converters.map import MapPolylineGridConverter, MapPolylineMapConverter
from app.views.PolylinePropertyView import PolylinePropertyView
from nicemvvm import nm
from nicemvvm.controls.GridView import GridView, GridViewColumn
from nicemvvm.controls.LeafletMap import LatLng
from nicemvvm.observables.Observable import Observable


def create_grid(view_model: Observable) -> GridView:
    polyline_converter = MapPolylineGridConverter()
    grid = (
        nm.gridview(
            row_selection="single",
            supress_auto_size=True,
        )
        .classes("h_full h-full")
        .bind(view_model, "polylines", "items", converter=polyline_converter)
        .bind(
            view_model,
            "selected_polyline",
            "selected_item",
            converter=polyline_converter,
        )
    )
    grid.columns = [
        GridViewColumn(
            header="Trip",
            field="traj_id",
            filter=True,
            width=60,
        ),
        GridViewColumn(header="Vehicle", field="vehicle_id", filter=True, width=60),
        GridViewColumn(header="Trace", field="trace_name", filter=True, width=60),
        GridViewColumn(header="km", field="km", filter=True, width=60),
    ]
    grid.row_id = "polyline_id"
    return grid


async def setup_map(m: ui.leaflet) -> None:
    await m.initialized()

    m.fit_bounds(
        bounds=[
            LatLng(42.2203052778, -83.8042902778),
            LatLng(42.3258, -83.674),
        ]
    )


def create_map(view_model: Observable) -> ui.leaflet:
    m = (
        nm.leaflet()
            .classes("h-full w-full")
            .bind(view_model, "zoom", "zoom")
            .bind(view_model, "center", "center")
            .bind(
                view_model,
                "polylines",
                "polylines",
                converter=MapPolylineMapConverter(),
            )
    )
    asyncio.create_task(setup_map(m))
    return m


def create_property_view(view_model: Observable) -> PolylinePropertyView:
    view = PolylinePropertyView(view_model).classes("w-full h-full")
    return view


class MapView(ui.column):
    def __init__(self, view_model: Observable):
        super().__init__()
        view_model.register(self._listener)

        with ui.splitter(horizontal=True, value=80).classes(
            "w-full h-full"
        ) as main_splitter:
            with main_splitter.before:
                self._map = create_map(view_model)

            with main_splitter.after:
                with ui.splitter(horizontal=False, value=80).classes(
                    "w-full h-full"
                ) as property_splitter:
                    with property_splitter.after:
                        self._property_view = create_property_view(view_model)
                    with property_splitter.before:
                        self._grid = create_grid(view_model)

            # Make sure the map is correctly resized
            main_splitter.on_value_change(
                lambda _: self._map.invalidate_size(animate=True)
            )
            main_splitter.on(
                "resize", lambda _: self._map.invalidate_size(animate=True)
            )

    def _listener(self, action: str, args: Mapping[str, Any]) -> None:
        match action:
            case "property":
                name = args["name"]
                value = args["value"]

                if name == "bounds":
                    self._map.fit_bounds(value)
