from typing import Any, Dict

from app.viewmodels.MapViewModel import MapPolyline, MapViewModel
from nicemvvm.ValueConverter import ValueConverter
from nicemvvm.controls.LeafletMap import Polyline
from nicemvvm.observables.Observable import Observable


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
        polyline = Polyline(
            layer_id=map_polyline.polyline_id,
            points=map_polyline.locations,
            color=map_polyline.color,
            weight=map_polyline.weight,
            opacity=map_polyline.opacity
        )
        return polyline