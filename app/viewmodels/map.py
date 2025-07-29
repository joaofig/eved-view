import uuid
from typing import Any, Dict, List, Tuple

from nicegui.run import process_pool
from shapely.geometry import point

from app.converters.general import NotNoneValueConverter
from app.models.trip import Trip, TripModel
from app.viewmodels.circle import MapCircle
from app.viewmodels.polygon import MapPolygon
from app.viewmodels.polyline import MapPolyline
from app.viewmodels.shape import MapShape
from nicemvvm.command import Command, RelayCommand
from nicemvvm.controls.leaflet.types import LatLng
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
        self._bounds: List[LatLng] = list()
        self._context_location: LatLng | None = None
        
        # Cache for faster trace lookup
        self._trace_cache: Dict[str, bool] = {}

        self._polygon_counter: int = 1

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
            t for t in self._polylines
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

    def geo_select_shape(self, pt: LatLng | None) -> None:
        self.selected_polygon = None
        self.selected_circle = None

        if pt is not None:
            shape = self.find_shape(pt)
            # print(f"Geo-selected shape: {shape}")
            self.selected_shape = shape
            if shape is not None:
                if isinstance(shape, MapPolygon):
                    self.selected_polygon = shape
                elif isinstance(shape, MapCircle):
                    self.selected_circle = shape

    def show_circle(self, circle: Dict) -> None:
        options = circle["options"]
        center = LatLng(circle["_latlng"]["lat"], circle["_latlng"]["lng"])
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

    def show_polyline(self, trip: Trip, trace_name: str) -> None:
        if not self._has_trace(trip, trace_name):
            match trace_name:
                case "gps":
                    color = "#0000FF"
                    locations = [LatLng(p.lat, p.lon) for p in trip.signals]
                case "match":
                    color = "#FF0000"
                    locations = [LatLng(p.match_lat, p.match_lon) for p in trip.signals]
                case "nodes":
                    color = "#00FF00"
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
            # self.selected_polyline = poly
            self.bounds = locations

    def _fit_content(self) -> Any:
        bounds = []
        for polyline in self.polylines:
            bounds.extend(polyline.locations)
        for polygon in self.polygons:
            bounds.extend(polygon.locations)
        if len(bounds) > 0:
            self.bounds = bounds
        else:
            self.bounds = [
                LatLng(42.2203052778, -83.8042902778),
                LatLng(42.3258, -83.674),
            ]

    @property
    def fit_content_command(self) -> Command:
        return RelayCommand(lambda _: self._fit_content())

    @property
    def remove_route_command(self) -> Command:
        return RemoveRouteCommand(self)

    @property
    def remove_area_command(self) -> Command:
        return RemoveAreaCommand(self)

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

    @property
    def remove_circle_command(self) -> Command:
        return RemoveCircleCommand(self)

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

    def _select_shape(self, arg: Any = None) -> Any:
        if isinstance(arg, LatLng):
            pt: LatLng = arg
            # print(f"Selecting shape at {pt}")
            self.geo_select_shape(pt)

    @property
    def select_shape_command(self) -> Command:
        return RelayCommand(self._select_shape)

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
    def bounds(self) -> List[LatLng]:
        return self._bounds

    @bounds.setter
    @notify_change
    def bounds(self, value: List[LatLng]) -> None:
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
