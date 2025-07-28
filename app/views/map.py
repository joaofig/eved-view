import asyncio
from typing import Any, Mapping

from nicegui import ui
from nicegui.events import GenericEventArguments

from app.converters.general import NotNoneValueConverter
from app.converters.map import (
    MapCircleMapConverter,
    MapPolygonGridConverter,
    MapPolygonMapConverter,
    MapPolylineGridConverter,
    MapPolylineMapConverter, MapCircleGridConverter,
)
from app.views.editors.circle import CirclePropertyEditor
from app.views.editors.polygon import PolygonPropertyEditor
from app.views.editors.polyline import PolylinePropertyEditor
from nicemvvm import nm
from nicemvvm.command import Command
from nicemvvm.controls.grid_view import GridView, GridViewColumn
from nicemvvm.controls.leaflet.map import LeafletMap
from nicemvvm.controls.leaflet.types import LatLng
from nicemvvm.controls.menu import MenuItem
from nicemvvm.observables.observability import Observable, Observer


class VerticalTabView(ui.column):
    def __init__(self):
        super().__init__()

        with self:
            with ui.tabs().props("vertical").classes("w-full") as tabs:
                routes_tab = ui.tab(
                    name="routes", label="Routes", icon="route"
                ).props("no-caps")
                areas_tab = ui.tab(
                    name="areas", label="Areas", icon="pentagon"
                ).props("no-caps")
                circles_tab = ui.tab(
                    name="circles", label="Circles", icon="brightness_1"
                ).props("no-caps")

        self._tabs = tabs
        self._routes_tab = routes_tab
        self._areas_tab = areas_tab
        self._circles_tab = circles_tab

    @property
    def tabs(self) -> ui.tabs:
        return self._tabs

    @property
    def routes_tab(self) -> ui.tab:
        return self._routes_tab

    @property
    def areas_tab(self) -> ui.tab:
        return self._areas_tab

    @property
    def circles_tab(self) -> ui.tab:
        return self._circles_tab


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


def create_area_grid(view_model: Observable) -> GridView:
    polygon_converter = MapPolygonGridConverter()
    grid = (
        nm.gridview(
            row_selection="single",
            supress_auto_size=True,
        )
        .classes("h_full h-full")
        .bind(view_model, "polygons", "items",
              converter=polygon_converter)
        .bind(view_model, "selected_polygon", "selected_item",
              converter=polygon_converter)
    )
    grid.columns = [
        GridViewColumn(
            header="ID",
            field="shape_id",
            filter=True,
            width=60,
        ),
        GridViewColumn(header="Vertices", field="vertices", filter=True, width=60),
    ]
    grid.row_id = "shape_id"
    return grid


def create_circle_grid(view_model: Observable) -> GridView:
    circle_converter = MapCircleGridConverter()
    grid = (
        nm.gridview(row_selection="single", supress_auto_size=True,)
        .classes("h_full h-full")
        .bind(view_model, "circles", "items",
              converter=circle_converter)
        .bind(view_model, "selected_circle",
              "selected_item",
              converter=circle_converter)
    )
    grid.columns = [
        GridViewColumn(
            header="ID",
            field="shape_id",
            filter=True,
            width=60,
        ),
        GridViewColumn(header="Radius", field="radius", filter=True, width=60),
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


def create_map(view_model: Observable) -> LeafletMap:
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
        nm.leaflet(draw_control=draw_control,
                   hide_drawn_items=True,
                   )
            .classes("h-full w-full")
            .bind(view_model, "zoom", "zoom")
            .bind(view_model, "center", "center")
            .bind(view_model, "polylines", "polylines", converter=MapPolylineMapConverter())
            .bind(view_model, "polygons", "polygons", converter=MapPolygonMapConverter())
            .bind(view_model, "circles", "circles", converter=MapCircleMapConverter())
            .bind(view_model, "select_shape_command", "click_command")
    )
    asyncio.create_task(setup_map(m))
    return m


class MapView(ui.column, Observer):
    _map: LeafletMap
    add_area_to_map: Command | None = None
    add_circle_to_map: Command | None = None

    remove_route_command: Command | None = None
    remove_area_command: Command | None = None
    remove_circle_command: Command | None = None

    def __init__(self, view_model: Observable):
        super().__init__()
        self._context_menu: ui.context_menu | None = None
        self._ctx_latlng: LatLng | None = None

        view_model.register(self._listener)
        self.bind(view_model, "add_area_to_map_command", "add_area_to_map")
        self.bind(view_model, "add_circle_to_map_command", "add_circle_to_map")
        self.bind(view_model, "remove_route_command", "remove_route_command")
        self.bind(view_model, "remove_area_command", "remove_area_command")
        self.bind(view_model, "remove_circle_command", "remove_circle_command")
        self.bind(view_model, "bounds", "bounds")

        main_splitter = ui.splitter(horizontal=True, value=70)
        main_splitter.classes("w-full h-full")
        with main_splitter:
            with main_splitter.before:
                self._map = create_map(view_model)
                self._map.on("draw:created", self._handle_draw)
                # self._map.on("contextmenu", self._handle_contextmenu)
                # self._map.on("click", self._handle_click)

                with ui.context_menu().classes("small-menu") as self._context_menu:
                    self._context_menu.on("before-show", self._context_menu_before)
                    # self._context_menu.on("show", lambda _: ui.notify(self._ctx_latlng))

                    MenuItem("Zoom In", on_click=lambda _: self._map.zoom_in())
                    MenuItem("Zoom Out", on_click=lambda _: self._map.zoom_out())
                    MenuItem("Fit to Content").bind(view_model, "fit_content_command", "command")
                    ui.separator()
                    MenuItem("Show LatLng", on_click=lambda _: ui.notify(self._ctx_latlng))
                    MenuItem("Remove Polygons").bind(view_model,
                                                     property_name="context_location",
                                                     local_name="visible",
                                                     converter=NotNoneValueConverter())

            with main_splitter.after:
                # Property view
                with ui.grid(columns="auto 1fr").classes("w-full h-full gap-0"):
                    vertical_tab = VerticalTabView().classes("h-full")

                    with ui.column().classes("h-full"):
                        self._tab_panels = (
                            ui.tab_panels(vertical_tab.tabs, value=vertical_tab.routes_tab)
                            .classes("w-full h-full")
                            .props("transition-prev=slide-down transition-next=slide-up")
                        )
                        with self._tab_panels:
                            with ui.tab_panel(vertical_tab.routes_tab).classes("w-full h-full p-0"):
                                # Route properties
                                with ui.splitter(horizontal=False, value=80) \
                                        .classes("w-full h-full") as route_splitter:
                                    with route_splitter.before:
                                        create_polyline_grid(view_model)

                                    with route_splitter.after:
                                        PolylinePropertyEditor(view_model,
                                                               remove_command=self.remove_route_command) \
                                            .classes("w-full h-full")

                            with ui.tab_panel(vertical_tab.areas_tab).classes("w-full h-full p-0"):
                                with ui.splitter(horizontal=False, value=80) \
                                        .classes("h-full w-full") as area_splitter:
                                    with area_splitter.before:
                                        create_area_grid(view_model).classes("w-full h-full")

                                    with area_splitter.after:
                                        PolygonPropertyEditor(view_model, remove_command=self.remove_area_command) \
                                            .classes("w-full h-full")

                            with ui.tab_panel(vertical_tab.circles_tab).classes("w-full h-full p-0"):
                                with ui.splitter(horizontal=False, value=80) \
                                        .classes("h-full w-full") as circle_splitter:
                                    with circle_splitter.before:
                                        create_circle_grid(view_model).classes("w-full h-full")

                                    with circle_splitter.after:
                                        CirclePropertyEditor(view_model, remove_command=self.remove_circle_command) \
                                            .classes("w-full h-full")

            # Make sure the map is correctly resized
            main_splitter.on_value_change(
                lambda _: self._map.invalidate_size(animate=True)
            )
            main_splitter.on(
                "resize", lambda _: self._map.invalidate_size(animate=True)
            )

    async def _context_menu_before(self, event: GenericEventArguments) -> None:
        x = event.args["clientX"]
        y = event.args["clientY"]
        ll = await self._map.run_map_method("containerPointToLatLng", [x, y])
        self._ctx_latlng = LatLng(ll["lat"], ll["lng"])
        self.propagate("context_location", self._ctx_latlng)

    @property
    def context_location(self) -> LatLng:
        return self._ctx_latlng

    def _handle_draw(self, event: GenericEventArguments) -> None:
        layer_type = event.args["layerType"]
        layer = event.args["layer"]
        match layer_type:
            case "polygon" | "rectangle":
                self.add_area_to_map.execute(layer)
                self._tab_panels.set_value("areas")
            case "circle":
                self.add_circle_to_map.execute(layer)
                self._tab_panels.set_value("circles")

    def _handle_click(self, event: GenericEventArguments) -> None:
        print(event)

    async def _handle_contextmenu(self, event: GenericEventArguments) -> None:
        # ui.notify(f"Map context menu: {event.args}")
        x = event.args["clientX"]
        y = event.args["clientY"]
        ll = await self._map.run_map_method("containerPointToLatLng", [x, y])
        self._ctx_latlng = LatLng(ll["lat"], ll["lng"])
        # print(self._ctx_latlng)

    def _listener(self, action: str, args: Mapping[str, Any]) -> None:
        # ui.notify(f"Map listener: {action} {args}")
        match action:
            case "property_changed":
                name = args["name"]
                value = args["value"]

                if name == "bounds":
                    self._map.fit_bounds(value)
                    # ui.notify(f"Map bounds set to {value}")