import unittest
from unittest.mock import Mock, patch

from app.converters.map import (
    MapPolylineGridConverter,
    MapPolygonGridConverter,
    MapPolylineMapConverter,
    MapPolygonMapConverter,
    MapCircleMapConverter,
)
from app.viewmodels.polyline import MapPolyline
from app.viewmodels.polygon import MapPolygon
from app.viewmodels.circle import MapCircle
from nicemvvm.controls.leaflet.types import LatLng
from nicemvvm.controls.leaflet.polyline import Polyline
from nicemvvm.controls.leaflet.polygon import Polygon
from nicemvvm.controls.leaflet.circle import Circle


class TestMapPolylineGridConverter(unittest.TestCase):
    def setUp(self):
        self.converter = MapPolylineGridConverter()
        self.locations = [
            LatLng(37.7749, -122.4194),
            LatLng(37.7849, -122.4094),
            LatLng(37.7949, -122.3994)
        ]
        self.polyline = MapPolyline(
            shape_id="test_polyline_1",
            traj_id=123,
            vehicle_id=456,
            km=5.5,
            color="#FF0000",
            weight=3.0,
            opacity=0.8,
            trace_name="gps",
            locations=self.locations
        )

    def test_convert_valid_polyline(self):
        result = self.converter.convert(self.polyline)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["shape_id"], "test_polyline_1")
        self.assertEqual(result["traj_id"], 123)
        self.assertEqual(result["vehicle_id"], 456)
        self.assertEqual(result["km"], 5.5)
        self.assertEqual(result["color"], "#FF0000")
        self.assertEqual(result["weight"], 3.0)
        self.assertEqual(result["opacity"], 0.8)
        self.assertEqual(result["trace_name"], "gps")
        self.assertEqual(result["locations"], self.locations)
        
        # Verify object is stored in internal map
        self.assertIn("test_polyline_1", self.converter._object_map)
        self.assertEqual(self.converter._object_map["test_polyline_1"], self.polyline)

    def test_convert_none_polyline(self):
        result = self.converter.convert(None)
        self.assertEqual(result, {})

    def test_reverse_convert(self):
        # First convert to store in object map
        self.converter.convert(self.polyline)
        
        # Test reverse convert
        input_dict = {"shape_id": "test_polyline_1"}
        result = self.converter.reverse_convert(input_dict)
        
        self.assertEqual(result, self.polyline)

    def test_reverse_convert_missing_key(self):
        input_dict = {"shape_id": "nonexistent_key"}
        
        with self.assertRaises(KeyError):
            self.converter.reverse_convert(input_dict)


class TestMapPolygonGridConverter(unittest.TestCase):
    def setUp(self):
        self.converter = MapPolygonGridConverter()
        self.locations = [
            LatLng(37.7749, -122.4194),
            LatLng(37.7849, -122.4094),
            LatLng(37.7949, -122.3994),
            LatLng(37.7749, -122.4194)  # Close the polygon
        ]
        self.polygon = MapPolygon(
            shape_id="test_polygon_1",
            color="#00FF00",
            weight=2.0,
            opacity=0.7,
            locations=self.locations,
            fill=True,
            fill_color="#00FF00",
            fill_opacity=0.3
        )

    def test_convert_valid_polygon(self):
        result = self.converter.convert(self.polygon)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["shape_id"], "test_polygon_1")
        self.assertEqual(result["color"], "#00FF00")
        self.assertEqual(result["weight"], 2.0)
        self.assertEqual(result["opacity"], 0.7)
        self.assertEqual(result["fill"], True)
        self.assertEqual(result["fill_color"], "#00FF00")
        self.assertEqual(result["fill_opacity"], 0.3)
        self.assertEqual(result["vertices"], len(self.locations))
        
        # Verify object is stored in internal map
        self.assertIn("test_polygon_1", self.converter._object_map)
        self.assertEqual(self.converter._object_map["test_polygon_1"], self.polygon)

    def test_convert_none_polygon(self):
        result = self.converter.convert(None)
        self.assertEqual(result, {})

    def test_reverse_convert(self):
        # First convert to store in object map
        self.converter.convert(self.polygon)
        
        # Test reverse convert
        input_dict = {"shape_id": "test_polygon_1"}
        result = self.converter.reverse_convert(input_dict)
        
        self.assertEqual(result, self.polygon)

    def test_reverse_convert_missing_key(self):
        input_dict = {"shape_id": "nonexistent_key"}
        
        with self.assertRaises(KeyError):
            self.converter.reverse_convert(input_dict)


class TestMapPolylineMapConverter(unittest.TestCase):
    def setUp(self):
        self.converter = MapPolylineMapConverter()
        self.locations = [
            LatLng(37.7749, -122.4194),
            LatLng(37.7849, -122.4094),
            LatLng(37.7949, -122.3994)
        ]
        self.polyline = MapPolyline(
            shape_id="test_polyline_1",
            traj_id=123,
            vehicle_id=456,
            km=5.5,
            color="#FF0000",
            weight=3.0,
            opacity=0.8,
            trace_name="gps",
            locations=self.locations
        )

    @patch('nicemvvm.controls.leaflet.polyline.Polyline')
    def test_convert(self, mock_polyline_class):
        mock_polyline = Mock(spec=Polyline)
        mock_polyline.bind.return_value = mock_polyline
        mock_polyline_class.return_value = mock_polyline
        
        result = self.converter.convert(self.polyline)
        
        # Verify Polyline was created with correct parameters
        mock_polyline_class.assert_called_once_with(
            layer_id="test_polyline_1",
            points=self.locations,
            color="#FF0000",
            weight=3.0,
            opacity=0.8
        )
        
        # Verify bindings were set up
        expected_bind_calls = [
            unittest.mock.call(self.polyline, "color", "color"),
            unittest.mock.call(self.polyline, "weight", "weight"),
            unittest.mock.call(self.polyline, "opacity", "opacity"),
        ]
        mock_polyline.bind.assert_has_calls(expected_bind_calls)
        
        self.assertEqual(result, mock_polyline)


class TestMapPolygonMapConverter(unittest.TestCase):
    def setUp(self):
        self.converter = MapPolygonMapConverter()
        self.locations = [
            LatLng(37.7749, -122.4194),
            LatLng(37.7849, -122.4094),
            LatLng(37.7949, -122.3994),
            LatLng(37.7749, -122.4194)  # Close the polygon
        ]
        self.polygon = MapPolygon(
            shape_id="test_polygon_1",
            color="#00FF00",
            weight=2.0,
            opacity=0.7,
            locations=self.locations,
            fill=True,
            fill_color="#00FF00",
            fill_opacity=0.3
        )

    @patch('nicemvvm.controls.leaflet.polygon.Polygon')
    def test_convert(self, mock_polygon_class):
        mock_polygon = Mock(spec=Polygon)
        mock_polygon.bind.return_value = mock_polygon
        mock_polygon_class.return_value = mock_polygon
        
        result = self.converter.convert(self.polygon)
        
        # Verify Polygon was created with correct parameters
        mock_polygon_class.assert_called_once_with(
            layer_id="test_polygon_1",
            points=self.locations,
            color="#00FF00",
            weight=2.0,
            opacity=0.7,
            fill=True,
            fill_color="#00FF00",
            fill_opacity=0.3
        )
        
        # Verify bindings were set up
        expected_bind_calls = [
            unittest.mock.call(self.polygon, "color", "color"),
            unittest.mock.call(self.polygon, "weight", "weight"),
            unittest.mock.call(self.polygon, "opacity", "opacity"),
            unittest.mock.call(self.polygon, "fill", "fill"),
            unittest.mock.call(self.polygon, "fill_color", "fill_color"),
            unittest.mock.call(self.polygon, "fill_opacity", "fill_opacity"),
        ]
        mock_polygon.bind.assert_has_calls(expected_bind_calls)
        
        self.assertEqual(result, mock_polygon)


class TestMapCircleMapConverter(unittest.TestCase):
    def setUp(self):
        self.converter = MapCircleMapConverter()
        self.center = LatLng(37.7749, -122.4194)
        self.circle = MapCircle(
            shape_id="test_circle_1",
            color="#0000FF",
            weight=1.5,
            opacity=0.9,
            center=self.center,
            radius=100.0,
            fill=True,
            fill_color="#0000FF",
            fill_opacity=0.2
        )

    @patch('nicemvvm.controls.leaflet.circle.Circle')
    def test_convert(self, mock_circle_class):
        mock_circle = Mock(spec=Circle)
        mock_circle.bind.return_value = mock_circle
        mock_circle_class.return_value = mock_circle
        
        result = self.converter.convert(self.circle)
        
        # Verify Circle was created with correct parameters
        mock_circle_class.assert_called_once_with(
            layer_id="test_circle_1",
            center=self.center,
            radius=100.0,
            color="#0000FF",
            weight=1.5,
            opacity=0.9,
            fill=True,
            fill_color="#0000FF",
            fill_opacity=0.2
        )
        
        # Verify bindings were set up
        expected_bind_calls = [
            unittest.mock.call(self.circle, "color", "color"),
            unittest.mock.call(self.circle, "weight", "weight"),
            unittest.mock.call(self.circle, "opacity", "opacity"),
            unittest.mock.call(self.circle, "fill", "fill"),
            unittest.mock.call(self.circle, "fill_color", "fill_color"),
            unittest.mock.call(self.circle, "fill_opacity", "fill_opacity"),
        ]
        mock_circle.bind.assert_has_calls(expected_bind_calls)
        
        self.assertEqual(result, mock_circle)


class TestMapConvertersIntegration(unittest.TestCase):
    """Integration tests for map converters working together."""
    
    def test_grid_converters_round_trip(self):
        """Test that grid converters can convert and reverse convert properly."""
        # Test polyline
        polyline_converter = MapPolylineGridConverter()
        locations = [LatLng(37.7749, -122.4194), LatLng(37.7849, -122.4094)]
        polyline = MapPolyline(
            shape_id="test_polyline",
            traj_id=123,
            vehicle_id=456,
            km=5.5,
            color="#FF0000",
            weight=3.0,
            opacity=0.8,
            trace_name="gps",
            locations=locations
        )
        
        # Convert to dict and back
        dict_result = polyline_converter.convert(polyline)
        reversed_polyline = polyline_converter.reverse_convert(dict_result)
        self.assertEqual(reversed_polyline, polyline)
        
        # Test polygon
        polygon_converter = MapPolygonGridConverter()
        polygon_locations = [
            LatLng(37.7749, -122.4194),
            LatLng(37.7849, -122.4094),
            LatLng(37.7949, -122.3994),
            LatLng(37.7749, -122.4194)
        ]
        polygon = MapPolygon(
            shape_id="test_polygon",
            color="#00FF00",
            weight=2.0,
            opacity=0.7,
            locations=polygon_locations,
            fill=True,
            fill_color="#00FF00",
            fill_opacity=0.3
        )
        
        # Convert to dict and back
        dict_result = polygon_converter.convert(polygon)
        reversed_polygon = polygon_converter.reverse_convert(dict_result)
        self.assertEqual(reversed_polygon, polygon)

    def test_converter_with_kwargs(self):
        """Test that converters handle keyword arguments properly."""
        converter = MapPolylineMapConverter(some_param="test")
        self.assertIsInstance(converter, MapPolylineMapConverter)
        
        converter = MapPolygonMapConverter(another_param=42)
        self.assertIsInstance(converter, MapPolygonMapConverter)
        
        converter = MapCircleMapConverter(test_kwarg=True)
        self.assertIsInstance(converter, MapCircleMapConverter)


if __name__ == '__main__':
    unittest.main()