from typing import Any, Dict

from app.viewmodels.MapViewModel import MapPolyline, MapPolygon
from nicemvvm.ValueConverter import ValueConverter
from nicemvvm.controls.leaflet.polygon import Polygon
from nicemvvm.controls.leaflet.polyline import Polyline


class MapPolylineGridConverter(ValueConverter):
    def __init__(self):
        super().__init__()
        self._object_map: Dict[str, MapPolyline] = dict()

    def convert(self, map_polyline: MapPolyline) -> Dict[str, Any]:
        if map_polyline:
            self._object_map[map_polyline.polyline_id] = map_polyline
            return map_polyline.to_dict()
        else:
            return {}

    def reverse_convert(self, value: Dict[str, Any]) -> MapPolyline:
        return self._object_map[value["polyline_id"]]


class MapPolylineValueConverter(ValueConverter):
    def __init__(self):
        super().__init__()
        self._object_map: Dict[str, MapPolyline] = dict()

    def convert(self, map_polyline: MapPolyline) -> Dict:
        self._object_map[map_polyline.polyline_id] = map_polyline
        return map_polyline.to_dict()

    def reverse_convert(self, value: Dict) -> MapPolyline:
        return self._object_map[value["polyline_id"]]


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
            )
            .bind(map_polygon, "color", "color")
            .bind(map_polygon, "weight", "weight")
            .bind(map_polygon, "opacity", "opacity")
        )
        return polygon
