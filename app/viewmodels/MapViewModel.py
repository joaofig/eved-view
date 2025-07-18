import uuid

from typing import Any, List, Tuple, Dict

from app.models.TripModel import Trip, TripModel
from nicemvvm.Command import Command
from nicemvvm.controls.leaflet.types import LatLng
from nicemvvm.observables.Observable import Observable, Observer, notify_change
from nicemvvm.observables.ObservableCollections import ObservableList
from nicemvvm.ResourceLocator import ResourceLocator
from nicemvvm.ValueConverter import ValueConverter


class MapShape(Observable):
    def __init__(
        self,
        shape_id: str,
        color: str,
        weight: float,
        opacity: float,
        fill: bool,
        fill_color: str,
        fill_opacity: float,
        locations: List[LatLng],
    ):
        super().__init__()
        self._shape_id = shape_id
        self._color = color
        self._weight = weight
        self._opacity = opacity
        self._fill = fill
        self._fill_color = fill_color
        self._fill_opacity = fill_opacity
        self._locations = locations

    @property
    def shape_id(self) -> str:
        return self._shape_id

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    @notify_change
    def color(self, value: str):
        self._color = value

    @property
    def weight(self) -> float:
        return self._weight

    @weight.setter
    @notify_change
    def weight(self, value: float):
        self._weight = value

    @property
    def opacity(self) -> float:
        return self._opacity

    @opacity.setter
    @notify_change
    def opacity(self, value: float):
        self._opacity = value

    @property
    def fill(self) -> bool:
        return self._fill

    @fill.setter
    @notify_change
    def fill(self, value: bool):
        self._fill = value

    @property
    def fill_color(self) -> str:
        return self._fill_color

    @fill_color.setter
    @notify_change
    def fill_color(self, value: str):
        self._fill_color = value

    @property
    def fill_opacity(self) -> float:
        return self._fill_opacity

    @fill_opacity.setter
    @notify_change
    def fill_opacity(self, value: float):
        self._fill_opacity = value

    @property
    def locations(self) -> List[LatLng]:
        return self._locations

    @locations.setter
    @notify_change
    def locations(self, value: List[LatLng]):
        self._locations = value


class MapPolyline(MapShape):
    def __init__(
        self,
        shape_id: str,
        traj_id: int,
        vehicle_id: int,
        km: float,
        color: str,
        weight: float,
        opacity: float,
        trace_name: str,
        locations: List[LatLng],
    ):
        super().__init__(
            shape_id,
            color=color,
            weight=weight,
            opacity=opacity,
            fill=False,
            fill_color=color,
            fill_opacity=opacity,
            locations=locations,
        )
        self._traj_id = traj_id
        self._vehicle_id = vehicle_id
        self._km = km
        self._trace_name = trace_name

    @property
    def traj_id(self) -> int:
        return self._traj_id

    @property
    def vehicle_id(self) -> int:
        return self._vehicle_id

    @property
    def km(self):
        return self._km

    @property
    def trace_name(self) -> str:
        return self._trace_name

    @trace_name.setter
    @notify_change
    def trace_name(self, value: str):
        self._trace_name = value

    def to_dict(self):
        return {
            "polyline_id": self._shape_id,
            "traj_id": self._traj_id,
            "vehicle_id": self._vehicle_id,
            "color": self._color,
            "weight": self._weight,
            "opacity": self._opacity,
            "trace_name": self._trace_name,
            "locations": self._locations,
            "km": self._km,
        }


class MapPolygon(MapShape):
    def __init__(
        self,
        shape_id: str,
        color: str,
        weight: float,
        opacity: float,
        locations: List[LatLng],
        fill: bool = True,
        fill_color: str = "",
        fill_opacity: float = 0.2,
    ):
        super().__init__(
            shape_id=shape_id,
            color=color,
            weight=weight,
            opacity=opacity,
            fill=fill,
            fill_color=color if not fill_color else fill_color,
            fill_opacity=fill_opacity,
            locations=locations,
        )

    def to_dict(self):
        return {
            "polygon_id": self._shape_id,
            "color": self._color,
            "weight": self._weight,
            "opacity": self._opacity,
            "fill": self._fill,
            "fill_color": self._fill_color,
            "fill_opacity": self._fill_opacity,
        }


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
        self._selected_trip_id: str = ""
        self._selected_polyline: MapPolyline | None = None
        self._polylines: ObservableList[MapPolyline] = ObservableList()
        self._selected_polygons: MapPolygon | None = None
        self._polygons: ObservableList[MapPolygon] = ObservableList()
        self._bounds: List[LatLng] = list()

    def _has_trace(self, trip: Trip, trace_name: str) -> bool:
        return any(
            t
            for t in self._polylines
            if t.traj_id == trip.traj_id and t.trace_name == trace_name
        )

    def show_draw_polygon(self, draw_polygon: Dict) -> None:
        options = draw_polygon["options"]
        locations = [LatLng(ll["lat"], ll["lng"]) for ll in draw_polygon["_latlngs"][0]]
        poly = MapPolygon(
            shape_id=str(uuid.uuid4()),
            color=options["color"],
            weight=options["weight"],
            opacity=options["opacity"],
            fill=options["fill"],
            fill_color=options["fillColor"],
            fill_opacity=options["fillOpacity"],
            locations=locations,
        )
        self._polygons.append(poly)
        self.bounds = locations
        return None

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
        if trip is not None:
            self.selected_trip_id = str(trip.traj_id)
        else:
            self.selected_trip_id = ""

    @property
    def selected_trip_id(self) -> str:
        return self._selected_trip_id

    @selected_trip_id.setter
    @notify_change
    def selected_trip_id(self, trip_id: str) -> None:
        self._selected_trip_id = trip_id

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
            self._view_model.show_draw_polygon(draw_polygon)
        return None
