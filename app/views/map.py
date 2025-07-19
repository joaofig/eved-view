import asyncio
from typing import Any, Mapping

from nicegui import ui
from nicegui.events import GenericEventArguments

from app.converters.map import (
    MapPolylineGridConverter,
    MapPolylineMapConverter,
    MapPolygonMapConverter, MapCircleMapConverter,
)
from app.views.polygon import PolygonPropertyEditor
from app.views.polyline import PolylinePropertyEditor
from nicemvvm import nm
from nicemvvm.command import Command
from nicemvvm.controls.grid_view import GridView, GridViewColumn
from nicemvvm.controls.leaflet.types import LatLng
from nicemvvm.observables.observability import Observable, Observer


def create_polyline_grid(view_model: Observable) -> GridView:
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
    grid.row_id = "shape_id"
    return grid


def create_route_property_editor(view_model: Observable) -> PolylinePropertyEditor:
    view = PolylinePropertyEditor(view_model).classes("w-full h-full")
    return view


def create_area_grid(view_model: Observable) -> GridView:
    grid = (
        nm.gridview(
            row_selection="single",
            supress_auto_size=True,
        )
        .classes("h_full h-full")
        .bind(view_model, "polygons", "items")
        .bind(view_model, "selected_polygon", "selected_item")
    )
    grid.columns = [
        GridViewColumn(header="ID", field="shape_id", filter=True, width=60,),
        GridViewColumn(header="Vertices", field="vertices", filter=True, width=60),
    ]
    grid.row_id = "shape_id"
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
    draw_control = {
        "position": "topleft",
        "draw": {
            "polygon": True,
            "polyline": False,
            "rectangle": True,
            "circle": True,
            "marker": False,
            "circlemarker": False,
        },
        "edit": False,
    }
    m = (
        nm.leaflet(draw_control=draw_control, hide_drawn_items=True)
        .classes("h-full w-full")
        .bind(view_model, "zoom", "zoom")
        .bind(view_model, "center", "center")
        .bind(view_model, "polylines", "polylines", converter=MapPolylineMapConverter())
        .bind(view_model, "polygons", "polygons", converter=MapPolygonMapConverter())
        .bind(view_model, "circles", "circles", converter=MapCircleMapConverter())
    )
    asyncio.create_task(setup_map(m))
    return m


class MapView(ui.column, Observer):
    add_area_to_map: Command | None = None
    add_circle_to_map: Command | None = None

    def __init__(self, view_model: Observable):
        super().__init__()
        view_model.register(self._listener)
        self.bind(view_model, "add_area_to_map_command", "add_area_to_map")
        self.bind(view_model, "add_circle_to_map_command", "add_circle_to_map")

        with (ui.splitter(horizontal=True, value=70).classes(
            "w-full h-full"
        ) as main_splitter):
            with main_splitter.before:
                self._map = create_map(view_model)
                self._map.on("draw:created", self._handle_draw)

            with main_splitter.after:
                # Property view
                with ui.grid(columns="auto 1fr").classes("w-full h-full gap-0"):
                    with ui.column().classes("h-full"):
                        with ui.tabs().props("vertical").classes("w-full") as tabs:
                            routes_tab = ui.tab(
                                name="routes", label="Routes", icon="route"
                            ).props("no-caps")
                            areas_tab = ui.tab(
                                name="areas", label="Areas", icon="pentagon"
                            ).props("no-caps")
                            circles_tab = ui.tab(name="circles", label="Circles", icon="brightness_1").props("no-caps")
                    with ui.column().classes("h-full"):

                        with ui.tab_panels(tabs, value=routes_tab).classes("w-full h-full") \
                                    .props("transition-prev=slide-down transition-next=slide-up"):
                            with ui.tab_panel(routes_tab).classes("w-full h-full p-0"):
                                # Route properties
                                with ui.splitter(horizontal=False, value=80) \
                                        .classes("w-full h-full") as route_splitter:
                                    with route_splitter.after:
                                        self._property_editor = create_route_property_editor(view_model)
                                    with route_splitter.before:
                                        self._polyline_grid = create_polyline_grid(view_model)

                            with ui.tab_panel(areas_tab).classes("w-full h-full p-0"):
                                with ui.splitter(horizontal=False, value=80) \
                                        .classes("h-full w-full") as area_splitter:
                                    with area_splitter.before:
                                        self._area_grid = create_area_grid(view_model)
                                        self._area_grid.classes("w-full h-full")
                                    with area_splitter.after:
                                        self._area_editor = PolygonPropertyEditor(view_model)
                                        self._area_editor.classes("w-full h-full")

                            with ui.tab_panel(circles_tab).classes("w-full h-full p-0"):
                                ui.label("Not implemented yet")

            # Make sure the map is correctly resized
            main_splitter.on_value_change(
                lambda _: self._map.invalidate_size(animate=True)
            )
            main_splitter.on(
                "resize", lambda _: self._map.invalidate_size(animate=True)
            )

    def _handle_draw(self, event: GenericEventArguments) -> None:
        layer_type = event.args["layerType"]
        layer = event.args["layer"]
        match layer_type:
            case "polygon" | "rectangle":
                self.add_area_to_map.execute(layer)
            case "circle":
                self.add_circle_to_map.execute(layer)

    def _listener(self, action: str, args: Mapping[str, Any]) -> None:
        match action:
            case "property_changed":
                name = args["name"]
                value = args["value"]

                if name == "bounds":
                    self._map.fit_bounds(value)
