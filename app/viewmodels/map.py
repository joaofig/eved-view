import uuid
from functools import reduce
from typing import Any, Dict, Tuple

import h3.api.numpy_int as h3

from app.converters.general import NotNoneValueConverter
from app.models.trip import Trip, TripModel
from app.viewmodels.circle import MapCircle
from app.viewmodels.polygon import MapPolygon
from app.viewmodels.polyline import MapPolyline
from app.viewmodels.shape import MapShape
from nicemvvm.command import Command, RelayCommand
from nicemvvm.controls.leaflet.types import GeoBounds, LatLng
from nicemvvm.observables.collections import ObservableList
from nicemvvm.observables.observability import Observable, Observer, notify_change
from nicemvvm.ResourceLocator import ResourceLocator


class MapViewModel(Observable):
    def __init__(self):
        super().__init__()
        self._zoom = 10
        self._center: Tuple[float, float] = (0.0, 0.0)
        self._locator = ResourceLocator()
        self._trip_model: TripModel = self._locator["TripModel"]
        self._trips: ObservableList[Trip] = ObservableList(self._trip_model.load())
        self._selected_trip: Trip | None = None
        self._selected_polyline: MapPolyline | None = None
        self._polylines: ObservableList[MapPolyline] = ObservableList()
        self._selected_polygon: MapPolygon | None = None
        self._polygons: ObservableList[MapPolygon] = ObservableList()
        self._selected_circle: MapCircle | None = None
        self._circles: ObservableList[MapCircle] = ObservableList()
        self._selected_shape: MapShape | None = None
        self._bounds: GeoBounds | None = None
        self._content_bounds: GeoBounds | None = None
        self._context_location: LatLng | None = None

        self._polyline_map: dict[str, MapPolyline] = dict()
        self._polygon_map: dict[str, MapPolygon] = dict()
        self._circle_map: dict[str, MapCircle] = dict()

        # Cache for faster trace lookup
        self._trace_cache: Dict[str, bool] = {}

        self._polygon_counter: int = 1

    def _merge_bounds(self, bounds: GeoBounds) -> None:
        if self._content_bounds is None:
            self._content_bounds = bounds
        else:
            self._content_bounds.merge(bounds)

    def _has_trace(self, trip: Trip, trace_name: str) -> bool:
        """
        Check if a trace exists for the given trip and trace name.
        Uses a cache for better performance.

        :param trip: The trip to check
        :param trace_name: The name of the trace
        :return: True if the trace exists, False otherwise
        """
        # Create a unique key for the cache
        cache_key = f"{trip.traj_id}_{trace_name}"

        # Check the cache first
        if cache_key in self._trace_cache:
            return self._trace_cache[cache_key]

        # If not in cache, do the lookup
        result = any(
            t
            for t in self._polylines
            if t.traj_id == trip.traj_id and t.trace_name == trace_name
        )

        # Cache the result
        self._trace_cache[cache_key] = result
        return result

    def find_shape(self, pt: LatLng) -> MapShape | None:
        for polygon in self.polygons:
            if polygon.contains(pt):
                return polygon
        for circle in self.circles:
            if circle.contains(pt):
                return circle
        return None

    def select_polyline(self, layer_id: str) -> None:
        if layer_id in self._polyline_map:
            self.selected_polyline = self._polyline_map[layer_id]
            self.selected_polygon = None
            self.selected_circle = None

    def select_polygon(self, layer_id: str) -> None:
        if layer_id in self._polygon_map:
            self.selected_polygon = self._polygon_map[layer_id]
            self.selected_polyline = None
            self.selected_circle = None

    def select_circle(self, layer_id: str) -> None:
        if layer_id in self._circle_map:
            self.selected_circle = self._circle_map[layer_id]
            self.selected_polyline = None
            self.selected_polygon = None

    def geo_select_shape(self, pt: LatLng | None) -> None:
        if pt is not None:
            shape = self.find_shape(pt)
            self.selected_shape = shape
            if shape is not None:
                if isinstance(shape, MapPolygon):
                    self.selected_polygon = shape
                    self.selected_circle = None
                elif isinstance(shape, MapCircle):
                    self.selected_circle = shape
                    self.selected_polygon = None

    def show_circle(self, circle: Dict) -> None:
        options = circle["options"]
        latlng = circle["_latlng"]
        lat = latlng["lat"]
        lng = latlng["lng"]
        center = LatLng(lat, lng)
        radius = circle["_mRadius"]
        circle = MapCircle(
            shape_id=str(uuid.uuid4()),
            color=options["color"],
            weight=options["weight"],
            opacity=options["opacity"],
            center=center,
            radius=radius,
            fill=options["fill"],
            fill_color=options["fillColor"],
            fill_opacity=options["fillOpacity"],
        )
        self._circles.append(circle)
        self._circle_map[circle.shape_id] = circle

    def show_polygon(self, draw_polygon: Dict) -> None:
        options = draw_polygon["options"]
        locations = [LatLng(ll["lat"], ll["lng"]) for ll in draw_polygon["_latlngs"][0]]
        poly = MapPolygon(
            shape_id=f"area-{self._polygon_counter}",
            color=options["color"],
            weight=options["weight"],
            opacity=options["opacity"],
            fill=options["fill"],
            fill_color=options["fillColor"],
            fill_opacity=options["fillOpacity"],
            locations=locations,
        )
        self._polygons.append(poly)
        self._polygon_counter += 1
        self._polygon_map[poly.shape_id] = poly

    def show_polyline(self, trip: Trip, trace_name: str) -> None:
        if not self._has_trace(trip, trace_name):
            match trace_name:
                case "gps":
                    color = "#800000"  # Dark Red
                    locations = [LatLng(p.lat, p.lon) for p in trip.signals]
                case "match":
                    color = "#000080"  # Dark Purple / Indigo
                    locations = [LatLng(p.match_lat, p.match_lon) for p in trip.signals]
                case "nodes":
                    color = "#004225"  # Dark Green
                    locations = [LatLng(n.lat, n.lon) for n in trip.nodes]
                case _:
                    locations = []
                    color = "#000000"

            poly = MapPolyline(
                shape_id=f"{trip.traj_id}_{trace_name}",
                traj_id=trip.traj_id,
                vehicle_id=trip.vehicle_id,
                color=color,
                weight=3.0,
                opacity=0.6,
                trace_name=trace_name,
                locations=locations,
                km=trip.km,
            )
            self._polylines.append(poly)
            self._polyline_map[poly.shape_id] = poly
            # self.selected_polyline = poly
            self.bounds = poly.get_bounds()

    def _fit_content(self) -> Any:
        def merge(a: GeoBounds, b: GeoBounds) -> GeoBounds:
            return a.merge(b)

        bounds = []
        bounds.extend([polyline.get_bounds() for polyline in self.polylines])
        bounds.extend([polygon.get_bounds() for polygon in self.polygons])
        bounds.extend([circle.get_bounds() for circle in self.circles])

        if len(bounds) > 0:
            self.bounds = reduce(merge, bounds)
        else:
            self.bounds = GeoBounds(
                LatLng(42.2203052778, -83.8042902778),
                LatLng(42.3258, -83.674),
            )

    @property
    def fit_content_command(self) -> Command:
        return RelayCommand(lambda _: self._fit_content())

    def _remove_polyline(self, layer_id: str) -> None:
        if not layer_id and self.selected_polyline is not None:
            layer_id = self.selected_polyline.shape_id

        if layer_id in self._polyline_map:
            polyline = self._polyline_map[layer_id]
            del self._polyline_map[layer_id]
            self._polylines.remove(polyline)
            self.selected_polyline = None

    @property
    def remove_route_command(self) -> Command:
        return RelayCommand(lambda layer_id: self._remove_polyline(layer_id))

    def _remove_polygon(self, layer_id: str) -> None:
        if not layer_id and self.selected_polygon is not None:
            layer_id = self.selected_polygon.shape_id

        if layer_id in self._polygon_map:
            polygon = self._polygon_map[layer_id]
            del self._polygon_map[layer_id]
            self._polygons.remove(polygon)
            self.selected_polygon = None

    @property
    def remove_area_command(self) -> Command:
        return RelayCommand(lambda layer_id: self._remove_polygon(layer_id))

    def _convert_area_to_h3(self, layer_id: str) -> None:
        if not layer_id and self.selected_polygon is not None:
            layer_id = self.selected_polygon.shape_id

        if layer_id in self._polygon_map:
            polygon = self._polygon_map[layer_id]
            h3_poly: h3.LatLngPoly = h3.LatLngPoly(
                [(ll.lat, ll.lng) for ll in polygon.locations]
            )
            h3_cells = h3.h3shape_to_cells_experimental(h3_poly, 12, contain="overlap")
            geo = h3.cells_to_geo(h3_cells, tight=True)
            coordinates = geo["coordinates"]

            # Coordinates are in (lng, lat) format.
            locations = [LatLng(ll[1], ll[0]) for ll in coordinates[0]]
            poly = MapPolygon(
                shape_id=f"area-{self._polygon_counter}",
                color=polygon.color,
                weight=polygon.weight,
                opacity=polygon.opacity,
                fill=polygon.fill,
                fill_color=polygon.fill_color,
                fill_opacity=polygon.fill_opacity,
                locations=locations,
            )
            self._polygons.append(poly)
            self._polygon_counter += 1
            self._polygon_map[poly.shape_id] = poly

    @property
    def convert_area_to_h3_command(self) -> Command:
        return RelayCommand(lambda layer_id: self._convert_area_to_h3(layer_id))

    def _remove_shape(self) -> None:
        if self.selected_shape is not None:
            map_polygon = self.selected_polygon
            if map_polygon is not None:
                self._polygons.remove(map_polygon)
                self.selected_polygon = None
                return
            map_circle = self.selected_circle
            if map_circle is not None:
                self._circles.remove(map_circle)
                self.selected_circle = None

    @property
    def remove_shape_command(self) -> Command:
        return RelayCommand(lambda _: self._remove_shape())

    def _remove_circle(self, layer_id: str) -> None:
        if not layer_id and self.selected_circle is not None:
            layer_id = self.selected_circle.shape_id

        if layer_id in self._circle_map:
            circle = self._circle_map[layer_id]
            del self._circle_map[layer_id]
            self._circles.remove(circle)
            self.selected_circle = None

    @property
    def remove_circle_command(self) -> Command:
        return RelayCommand(lambda layer_id: self._remove_circle(layer_id))

    def _add_area_to_map(self, arg: Any) -> None:
        if isinstance(arg, Dict):
            draw_polygon: Dict = arg
            self.show_polygon(draw_polygon)

    @property
    def add_area_to_map_command(self) -> Command:
        return RelayCommand(self._add_area_to_map)

    def _add_circle_to_map(self, arg: Any) -> None:
        if isinstance(arg, Dict):
            circle: Dict = arg
            self.show_circle(circle)

    @property
    def add_circle_to_map_command(self) -> Command:
        return RelayCommand(self._add_circle_to_map)

    @property
    def select_polyline_command(self) -> Command:
        return RelayCommand(lambda layer_id: self.select_polyline(layer_id))

    @property
    def select_polygon_command(self) -> Command:
        return RelayCommand(lambda layer_id: self.select_polygon(layer_id))

    @property
    def select_circle_command(self) -> Command:
        return RelayCommand(lambda layer_id: self.select_circle(layer_id))

    @property
    def zoom(self) -> int:
        return self._zoom

    @zoom.setter
    @notify_change
    def zoom(self, value: int) -> None:
        self._zoom = value

    @property
    def center(self) -> Tuple[float, float]:
        return self._center

    @center.setter
    @notify_change
    def center(self, value: Tuple[float, float]) -> None:
        self._center = value

    @property
    def context_location(self) -> LatLng | None:
        return self._context_location

    @context_location.setter
    @notify_change
    def context_location(self, value: LatLng | None) -> None:
        self._context_location = value
        self.geo_select_shape(value)

    @property
    def trips(self) -> ObservableList[Trip]:
        return self._trips

    @property
    def selected_trip(self) -> Trip | None:
        return self._selected_trip

    @selected_trip.setter
    @notify_change
    def selected_trip(self, trip: Trip | None) -> None:
        self._selected_trip = trip

    @property
    def polylines(self) -> ObservableList[MapPolyline]:
        return self._polylines

    @property
    def selected_polyline(self) -> MapPolyline | None:
        return self._selected_polyline

    @selected_polyline.setter
    @notify_change
    def selected_polyline(self, polyline: MapPolyline | None):
        self._selected_polyline = polyline

    @property
    def polygons(self) -> ObservableList[MapPolygon]:
        return self._polygons

    @property
    def selected_polygon(self) -> MapPolygon | None:
        return self._selected_polygon

    @selected_polygon.setter
    @notify_change
    def selected_polygon(self, polygon: MapPolygon | None):
        if self._selected_polygon is not None:
            self._selected_polygon.dash_array = ""
        self._selected_polygon = polygon
        if polygon is not None:
            polygon.dash_array = "8 8"

    @property
    def circles(self) -> ObservableList[MapCircle]:
        return self._circles

    @property
    def selected_circle(self) -> MapCircle | None:
        return self._selected_circle

    @selected_circle.setter
    @notify_change
    def selected_circle(self, circle: MapCircle | None):
        if self._selected_circle is not None:
            self._selected_circle.dash_array = ""
        self._selected_circle = circle
        if circle is not None:
            circle.dash_array = "8 8"

    @property
    def selected_shape(self) -> MapShape | None:
        return self._selected_shape

    @selected_shape.setter
    @notify_change
    def selected_shape(self, shape: MapShape | None):
        self._selected_shape = shape

    @property
    def bounds(self) -> GeoBounds:
        return self._bounds

    @bounds.setter
    @notify_change
    def bounds(self, value: GeoBounds) -> None:
        self._bounds = value


class RemoveRouteCommand(Command, Observer):
    def __init__(self, view_model: MapViewModel, **kwargs):
        super().__init__(**kwargs)
        self._view_model = view_model
        self.bind(
            view_model,
            property_name="selected_polyline",
            local_name="is_enabled",
            converter=NotNoneValueConverter(),
        )

    def execute(self, arg: Any = None) -> Any:
        map_polyline = self._view_model.selected_polyline
        if map_polyline is not None:
            self._view_model.polylines.remove(map_polyline)
            self._view_model.selected_polyline = None
        return None


class RemoveAreaCommand(Command, Observer):
    def __init__(self, view_model: MapViewModel, **kwargs):
        super().__init__(**kwargs)
        self._view_model = view_model
        self.bind(
            view_model,
            property_name="selected_polygon",
            local_name="is_enabled",
            converter=NotNoneValueConverter(),
        )

    def execute(self, arg: Any = None) -> Any:
        map_polygon = self._view_model.selected_polygon
        if map_polygon is not None:
            self._view_model.polygons.remove(map_polygon)
            self._view_model.selected_polygon = None
        return None


class RemoveCircleCommand(Command, Observer):
    def __init__(self, view_model: MapViewModel, **kwargs):
        super().__init__(**kwargs)
        self._view_model = view_model
        self.bind(
            view_model,
            property_name="selected_circle",
            local_name="is_enabled",
            converter=NotNoneValueConverter(),
        )

    def execute(self, arg: Any = None) -> Any:
        map_circle = self._view_model.selected_circle
        if map_circle is not None:
            self._view_model.circles.remove(map_circle)
            self._view_model.selected_circle = None
        return None
