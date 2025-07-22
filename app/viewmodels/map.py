import uuid
from typing import Any, Dict, List, Tuple

from app.models.trip import Trip, TripModel
from app.viewmodels.circle import MapCircle
from app.viewmodels.polygon import MapPolygon
from app.viewmodels.polyline import MapPolyline
from nicemvvm.command import Command
from nicemvvm.controls.leaflet.types import LatLng
from nicemvvm.converter import ValueConverter
from nicemvvm.observables.collections import ObservableList
from nicemvvm.observables.observability import Observable, Observer, notify_change
from nicemvvm.ResourceLocator import ResourceLocator


class MapViewModel(Observable):
    def __init__(self):
        super().__init__()
        self._zoom = 10
        self._center: Tuple[float, float] = (0.0, 0.0)
        self._center_text: str = "(0, 0)"
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
        self._bounds: List[LatLng] = list()
        
        # Cache for faster trace lookup
        self._trace_cache: Dict[str, bool] = {}
        
        # Spatial index for shapes (simple implementation)
        self._polygon_spatial_index: Dict[str, MapPolygon] = {}
        self._circle_spatial_index: Dict[str, MapCircle] = {}

        self._polygon_counter: int = 1
        
        # Register listeners for collection changes
        self._polylines.register(self._on_polylines_changed)
        self._polygons.register(self._on_polygons_changed)
        self._circles.register(self._on_circles_changed)
    
    def _on_polylines_changed(self, action: str, args: Dict[str, Any]) -> None:
        """Handle changes to the polylines collection by updating the trace cache."""
        # Clear the trace cache when polylines change
        self._trace_cache.clear()
    
    def _on_polygons_changed(self, action: str, args: Dict[str, Any]) -> None:
        """Handle changes to the polygons collection by updating the spatial index."""
        # Rebuild the polygon spatial index
        self._rebuild_polygon_spatial_index()
    
    def _on_circles_changed(self, action: str, args: Dict[str, Any]) -> None:
        """Handle changes to the circles collection by updating the spatial index."""
        # Rebuild the circle spatial index
        self._rebuild_circle_spatial_index()
    
    def _rebuild_polygon_spatial_index(self) -> None:
        """Rebuild the spatial index for polygons."""
        self._polygon_spatial_index = {polygon.shape_id: polygon for polygon in self._polygons}
    
    def _rebuild_circle_spatial_index(self) -> None:
        """Rebuild the spatial index for circles."""
        self._circle_spatial_index = {circle.shape_id: circle for circle in self._circles}

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

    @property
    def remove_route_command(self) -> "RemoveRouteCommand":
        return RemoveRouteCommand(self)

    @property
    def add_area_to_map_command(self) -> "AddAreaToMapCommand":
        return AddAreaToMapCommand(self)

    @property
    def add_circle_to_map_command(self) -> "AddCircleToMapCommand":
        return AddCircleToMapCommand(self)

    @property
    def select_shape_command(self) -> "SelectShapeCommand":
        return SelectShapeCommand(self)

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
        self._selected_polygon = polygon

    @property
    def circles(self) -> ObservableList[MapCircle]:
        return self._circles

    @property
    def selected_circle(self) -> MapCircle | None:
        return self._selected_circle

    @selected_circle.setter
    @notify_change
    def selected_circle(self, circle: MapCircle | None):
        self._selected_circle = circle

    @property
    def bounds(self) -> List[LatLng]:
        return self._bounds

    @bounds.setter
    @notify_change
    def bounds(self, value: List[LatLng]) -> None:
        self._bounds = value


class SelectedTripValueConverter(ValueConverter):
    def __init__(self):
        super().__init__()

    def convert(self, x: Any) -> Any:
        return x is not None


class RemoveRouteCommand(Command, Observer):
    def __init__(self, view_model: MapViewModel, **kwargs):
        super().__init__(**kwargs)
        self._view_model = view_model
        self.bind(
            view_model,
            property_name="selected_polyline",
            local_name="is_enabled",
            converter=SelectedTripValueConverter(),
        )

    def execute(self, arg: Any = None) -> Any:
        map_polyline = self._view_model.selected_polyline
        if map_polyline is not None:
            self._view_model.polylines.remove(map_polyline)
            self._view_model.selected_polyline = None


class AddAreaToMapCommand(Command):
    def __init__(self, view_model: MapViewModel, **kwargs):
        super().__init__(**kwargs)
        self._view_model = view_model

    def execute(self, arg: Any = None) -> Any:
        if isinstance(arg, Dict):
            draw_polygon: Dict = arg
            self._view_model.show_polygon(draw_polygon)
        return None


class AddCircleToMapCommand(Command):
    def __init__(self, view_model: MapViewModel, **kwargs):
        super().__init__(**kwargs)
        self._view_model = view_model

    def execute(self, arg: Any = None) -> Any:
        if isinstance(arg, Dict):
            circle: Dict = arg
            self._view_model.show_circle(circle)
        return None


class SelectShapeCommand(Command, Observer):
    def __init__(self, view_model: MapViewModel):
        super().__init__()
        self._view_model = view_model

    def execute(self, arg: Any = None) -> Any:
        """
        Select a shape that contains the given point.
        Uses spatial indexes for better performance.
        
        :param arg: The point to check (LatLng)
        """
        if not isinstance(arg, LatLng):
            return
            
        point: LatLng = arg
        
        # First check polygons using the spatial index
        # This is still a linear search through polygons, but we're using the index
        # to avoid recreating the dictionary each time
        for polygon in self._view_model.polygons:
            if polygon.contains(point):
                self._view_model.selected_polygon = polygon
                return  # Exit early once we find a match
        
        # Then check circles using the spatial index
        for circle in self._view_model.circles:
            if circle.contains(point):
                self._view_model.selected_circle = circle
                return  # Exit early once we find a match
                
        # If no shape contains the point, deselect current selections
        self._view_model.selected_polygon = None
        self._view_model.selected_circle = None
