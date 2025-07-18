import asyncio
from typing import Any, Mapping

from nicegui import ui
from nicegui.events import GenericEventArguments

from app.converters.map import (
    MapPolylineGridConverter,
    MapPolylineMapConverter,
    MapPolygonMapConverter,
)
from app.geo.geomath import circle_to_polygon
from app.views.PolylinePropertyView import PolylinePropertyView
from nicemvvm import nm
from nicemvvm.Command import Command
from nicemvvm.controls.GridView import GridView, GridViewColumn
from nicemvvm.controls.leaflet.types import LatLng
from nicemvvm.observables.Observable import Observable, Observer


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
        .bind(
            view_model,
            "polylines",
            "polylines",
            converter=MapPolylineMapConverter(),
        )
        .bind(view_model, "polygons", "polygons", converter=MapPolygonMapConverter())
    )
    asyncio.create_task(setup_map(m))
    return m


def create_property_view(view_model: Observable) -> PolylinePropertyView:
    view = PolylinePropertyView(view_model).classes("w-full h-full")
    return view


class MapView(ui.column, Observer):
    add_area_to_map: Command | None = None

    def __init__(self, view_model: Observable):
        super().__init__()
        view_model.register(self._listener)
        self.bind(view_model, "add_area_to_map_command", "add_area_to_map")

        with ui.splitter(horizontal=True, value=80).classes(
            "w-full h-full"
        ) as main_splitter:
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
                    with ui.column().classes("h-full") as content_column:
                        with ui.splitter(horizontal=False, value=80).classes(
                            "w-full h-full"
                        ) as property_splitter:
                            with property_splitter.after:
                                self._property_view = create_property_view(view_model)
                            with property_splitter.before:
                                self._grid = create_polyline_grid(view_model)

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
                center_lat = layer["_latlng"]["lat"]
                center_lng = layer["_latlng"]["lng"]
                radius = layer["_mRadius"]
                layer["_latlngs"] = [[{"lat": p[0], "lng": p[1]}
                                     for p in circle_to_polygon(center_lat,
                                                                center_lng,
                                                                radius,
                                                                num_points=720)]]
                self.add_area_to_map.execute(layer)

                # _latlng
                # _mRadius
            # ui.notify("Polygon!")
        # ui.notify(f"Draw event: {event.args}")
        # args:
        # layerType
        # layer: options, _bounds, _latlngs, editing

    def _listener(self, action: str, args: Mapping[str, Any]) -> None:
        match action:
            case "property_changed":
                name = args["name"]
                value = args["value"]

                if name == "bounds":
                    self._map.fit_bounds(value)
