from typing import Dict

from app.viewmodels.MapViewModel import MapPolyline
from nicemvvm.controls.LeafletMap import Polyline
from nicemvvm.ValueConverter import ValueConverter


class MapPolylineValueConverter(ValueConverter):
    @staticmethod
    def convert(map_polyline: MapPolyline) -> Polyline:
        """
        Converts a MapPolyLine object to a LeafletMap Polyline object.
        :param map_polyline: A MapPolyline object.
        :return: The LeafletMap Polyline object.
        """
        polyline = Polyline(
            layer_id=map_polyline.polyline_id,
            points=map_polyline.locations,
            color=map_polyline.color,
            weight=map_polyline.weight,
            opacity=map_polyline.opacity,
        )
        (
            polyline.bind(map_polyline, "color", "color")
            .bind(map_polyline, "weight", "weight")
            .bind(map_polyline, "opacity", "opacity")
        )
        return polyline


class MapPolylineGridConverter(ValueConverter):
    @staticmethod
    def convert(map_polyline: MapPolyline) -> Dict:
        return map_polyline.to_dict()
