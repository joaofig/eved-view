from typing import Any, Dict

from app.viewmodels.circle import MapCircle
from app.viewmodels.map import MapPolygon, MapPolyline
from nicemvvm.controls.leaflet.circle import Circle
from nicemvvm.controls.leaflet.polygon import Polygon
from nicemvvm.controls.leaflet.polyline import Polyline
from nicemvvm.converter import ValueConverter


class MapPolylineGridConverter(ValueConverter):
    def __init__(self):
        super().__init__()
        self._object_map: Dict[str, MapPolyline] = dict()

    def convert(self, map_polyline: MapPolyline | None) -> Dict[str, Any]:
        if map_polyline:
            self._object_map[map_polyline.shape_id] = map_polyline
            return map_polyline.to_dict()
        else:
            return {}

    def reverse_convert(self, value: Dict[str, Any]) -> MapPolyline:
        return self._object_map[value["shape_id"]]


class MapPolygonGridConverter(ValueConverter):
    def __init__(self):
        super().__init__()
        self._object_map: Dict[str, MapPolygon] = dict()

    def convert(self, map_polygon: MapPolygon | None) -> Dict[str, Any]:
        if map_polygon:
            self._object_map[map_polygon.shape_id] = map_polygon
            return map_polygon.to_dict()
        else:
            return {}

    def reverse_convert(self, value: Dict[str, Any]) -> MapPolygon:
        return self._object_map[value["shape_id"]]


class MapCircleGridConverter(ValueConverter):
    def __init__(self):
        super().__init__()
        self._object_map: Dict[str, MapCircle] = dict()

    def convert(self, map_circle: MapCircle | None) -> Dict[str, Any]:
        if map_circle:
            self._object_map[map_circle.shape_id] = map_circle
            return map_circle.to_dict()
        else:
            return {}

    def reverse_convert(self, value: Dict[str, Any]) -> MapCircle:
        return self._object_map[value["shape_id"]]


class MapPolylineMapConverter(ValueConverter):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def convert(self, map_polyline: MapPolyline) -> Polyline:
        polyline = (
            Polyline(
                layer_id=map_polyline.shape_id,
                points=map_polyline.locations,
                color=map_polyline.color,
                weight=map_polyline.weight,
                opacity=map_polyline.opacity,
            )
            .bind(map_polyline, "color", "color")
            .bind(map_polyline, "weight", "weight")
            .bind(map_polyline, "opacity", "opacity")
            .bind(map_polyline, "dash_array", "dash_array")
        )
        return polyline


class MapPolygonMapConverter(ValueConverter):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def convert(self, map_polygon: MapPolygon) -> Polygon:
        polygon = (
            Polygon(
                layer_id=map_polygon.shape_id,
                points=map_polygon.locations,
                color=map_polygon.color,
                weight=map_polygon.weight,
                opacity=map_polygon.opacity,
                fill=map_polygon.fill,
                fill_color=map_polygon.fill_color,
                fill_opacity=map_polygon.fill_opacity,
            )
            .bind(map_polygon, "color", "color")
            .bind(map_polygon, "weight", "weight")
            .bind(map_polygon, "opacity", "opacity")
            .bind(map_polygon, "fill", "fill")
            .bind(map_polygon, "fill_color", "fill_color")
            .bind(map_polygon, "fill_opacity", "fill_opacity")
            .bind(map_polygon, "dash_array", "dash_array")
        )
        return polygon


class MapCircleMapConverter(ValueConverter):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def convert(self, map_circle: MapCircle) -> Circle:
        circle = (
            Circle(
                layer_id=map_circle.shape_id,
                center=map_circle.center,
                radius=map_circle.radius,
                color=map_circle.color,
                weight=map_circle.weight,
                opacity=map_circle.opacity,
                fill=map_circle.fill,
                fill_color=map_circle.fill_color,
                fill_opacity=map_circle.fill_opacity,
            )
            .bind(map_circle, "color", "color")
            .bind(map_circle, "weight", "weight")
            .bind(map_circle, "opacity", "opacity")
            .bind(map_circle, "fill", "fill")
            .bind(map_circle, "fill_color", "fill_color")
            .bind(map_circle, "fill_opacity", "fill_opacity")
            .bind(map_circle, "dash_array", "dash_array")
        )
        return circle
