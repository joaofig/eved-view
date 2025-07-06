from typing import Any

from app.viewmodels.MapViewModel import MapPolyline
from nicemvvm.controls.LeafletMap import Polyline
from nicemvvm.ValueConverter import ValueConverter


class MapPolylineValueConverter(ValueConverter):
    @staticmethod
    def convert(polyline: MapPolyline) -> Any:
        """
        Converts a MapPolyLine object to a LeafletMap Polyline object.
        :param polyline: A MapPolyline object.
        :return: The LeafletMap Polyline object.
        """
        return Polyline(
            layer_id=polyline.trace_name,
            points=polyline.locations,
            color=polyline.color,
            weight=polyline.weight,
            opacity=polyline.opacity,
        )
