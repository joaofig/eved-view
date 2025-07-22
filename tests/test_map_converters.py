from unittest.mock import Mock, patch

import pytest

from app.converters.map import (
    MapCircleMapConverter,
    MapPolygonGridConverter,
    MapPolygonMapConverter,
    MapPolylineGridConverter,
    MapPolylineMapConverter,
)
from app.viewmodels.circle import MapCircle
from app.viewmodels.polygon import MapPolygon
from app.viewmodels.polyline import MapPolyline
from nicemvvm.controls.leaflet.circle import Circle
from nicemvvm.controls.leaflet.polygon import Polygon
from nicemvvm.controls.leaflet.polyline import Polyline
from nicemvvm.controls.leaflet.types import LatLng


# Fixtures
@pytest.fixture
def sample_locations():
    return [
        LatLng(37.7749, -122.4194),
        LatLng(37.7849, -122.4094),
        LatLng(37.7949, -122.3994),
    ]


@pytest.fixture
def polygon_locations():
    return [
        LatLng(37.7749, -122.4194),
        LatLng(37.7849, -122.4094),
        LatLng(37.7949, -122.3994),
        LatLng(37.7749, -122.4194),  # Close the polygon
    ]


@pytest.fixture
def sample_polyline(sample_locations):
    return MapPolyline(
        shape_id="test_polyline_1",
        traj_id=123,
        vehicle_id=456,
        km=5.5,
        color="#FF0000",
        weight=3.0,
        opacity=0.8,
        trace_name="gps",
        locations=sample_locations,
    )


@pytest.fixture
def sample_polygon(polygon_locations):
    return MapPolygon(
        shape_id="test_polygon_1",
        color="#00FF00",
        weight=2.0,
        opacity=0.7,
        locations=polygon_locations,
        fill=True,
        fill_color="#00FF00",
        fill_opacity=0.3,
    )


@pytest.fixture
def sample_circle():
    center = LatLng(37.7749, -122.4194)
    return MapCircle(
        shape_id="test_circle_1",
        color="#0000FF",
        weight=1.5,
        opacity=0.9,
        center=center,
        radius=100.0,
        fill=True,
        fill_color="#0000FF",
        fill_opacity=0.2,
    )


# MapPolylineGridConverter Tests
class TestMapPolylineGridConverter:
    def test_convert_valid_polyline(self, sample_polyline):
        converter = MapPolylineGridConverter()
        result = converter.convert(sample_polyline)

        assert isinstance(result, dict)
        assert result["shape_id"] == "test_polyline_1"
        assert result["traj_id"] == 123
        assert result["vehicle_id"] == 456
        assert result["km"] == 5.5
        assert result["color"] == "#FF0000"
        assert result["weight"] == 3.0
        assert result["opacity"] == 0.8
        assert result["trace_name"] == "gps"
        assert result["locations"] == sample_polyline.locations

        # Verify object is stored in internal map
        assert "test_polyline_1" in converter._object_map
        assert converter._object_map["test_polyline_1"] == sample_polyline

    def test_convert_none_polyline(self):
        converter = MapPolylineGridConverter()
        result = converter.convert(None)
        assert result == {}

    def test_reverse_convert(self, sample_polyline):
        converter = MapPolylineGridConverter()

        # First convert to store in object map
        converter.convert(sample_polyline)

        # Test reverse convert
        input_dict = {"shape_id": "test_polyline_1"}
        result = converter.reverse_convert(input_dict)

        assert result == sample_polyline

    def test_reverse_convert_missing_key(self):
        converter = MapPolylineGridConverter()
        input_dict = {"shape_id": "nonexistent_key"}

        with pytest.raises(KeyError):
            converter.reverse_convert(input_dict)


# MapPolygonGridConverter Tests
class TestMapPolygonGridConverter:
    def test_convert_valid_polygon(self, sample_polygon):
        converter = MapPolygonGridConverter()
        result = converter.convert(sample_polygon)

        assert isinstance(result, dict)
        assert result["shape_id"] == "test_polygon_1"
        assert result["color"] == "#00FF00"
        assert result["weight"] == 2.0
        assert result["opacity"] == 0.7
        assert result["fill"] is True
        assert result["fill_color"] == "#00FF00"
        assert result["fill_opacity"] == 0.3
        assert result["vertices"] == len(sample_polygon.locations)

        # Verify object is stored in internal map
        assert "test_polygon_1" in converter._object_map
        assert converter._object_map["test_polygon_1"] == sample_polygon

    def test_convert_none_polygon(self):
        converter = MapPolygonGridConverter()
        result = converter.convert(None)
        assert result == {}

    def test_reverse_convert(self, sample_polygon):
        converter = MapPolygonGridConverter()

        # First convert to store in object map
        converter.convert(sample_polygon)

        # Test reverse convert
        input_dict = {"shape_id": "test_polygon_1"}
        result = converter.reverse_convert(input_dict)

        assert result == sample_polygon

    def test_reverse_convert_missing_key(self):
        converter = MapPolygonGridConverter()
        input_dict = {"shape_id": "nonexistent_key"}

        with pytest.raises(KeyError):
            converter.reverse_convert(input_dict)


# MapPolylineMapConverter Tests
class TestMapPolylineMapConverter:
    @patch("app.converters.map.Polyline")
    def test_convert(self, mock_polyline_class, sample_polyline):
        converter = MapPolylineMapConverter()
        mock_polyline = Mock(spec=Polyline)
        mock_polyline.bind.return_value = mock_polyline
        mock_polyline_class.return_value = mock_polyline

        result = converter.convert(sample_polyline)

        # Verify Polyline was created with correct parameters
        mock_polyline_class.assert_called_once_with(
            layer_id="test_polyline_1",
            points=sample_polyline.locations,
            color="#FF0000",
            weight=3.0,
            opacity=0.8,
        )

        # Verify bindings were set up
        expected_bind_calls = [
            (sample_polyline, "color", "color"),
            (sample_polyline, "weight", "weight"),
            (sample_polyline, "opacity", "opacity"),
        ]

        assert mock_polyline.bind.call_count == 3
        for expected_call in expected_bind_calls:
            mock_polyline.bind.assert_any_call(*expected_call)

        assert result == mock_polyline


# MapPolygonMapConverter Tests
class TestMapPolygonMapConverter:
    @patch("app.converters.map.Polygon")
    def test_convert(self, mock_polygon_class, sample_polygon):
        converter = MapPolygonMapConverter()
        mock_polygon = Mock(spec=Polygon)
        mock_polygon.bind.return_value = mock_polygon
        mock_polygon_class.return_value = mock_polygon

        result = converter.convert(sample_polygon)

        # Verify Polygon was created with correct parameters
        mock_polygon_class.assert_called_once_with(
            layer_id="test_polygon_1",
            points=sample_polygon.locations,
            color="#00FF00",
            weight=2.0,
            opacity=0.7,
            fill=True,
            fill_color="#00FF00",
            fill_opacity=0.3,
        )

        # Verify bindings were set up
        expected_bind_calls = [
            (sample_polygon, "color", "color"),
            (sample_polygon, "weight", "weight"),
            (sample_polygon, "opacity", "opacity"),
            (sample_polygon, "fill", "fill"),
            (sample_polygon, "fill_color", "fill_color"),
            (sample_polygon, "fill_opacity", "fill_opacity"),
        ]

        assert mock_polygon.bind.call_count == 6
        for expected_call in expected_bind_calls:
            mock_polygon.bind.assert_any_call(*expected_call)

        assert result == mock_polygon


# MapCircleMapConverter Tests
class TestMapCircleMapConverter:
    @patch("app.converters.map.Circle")
    def test_convert(self, mock_circle_class, sample_circle):
        converter = MapCircleMapConverter()
        mock_circle = Mock(spec=Circle)
        mock_circle.bind.return_value = mock_circle
        mock_circle_class.return_value = mock_circle

        result = converter.convert(sample_circle)

        # Verify Circle was created with correct parameters
        mock_circle_class.assert_called_once_with(
            layer_id="test_circle_1",
            center=sample_circle.center,
            radius=100.0,
            color="#0000FF",
            weight=1.5,
            opacity=0.9,
            fill=True,
            fill_color="#0000FF",
            fill_opacity=0.2,
        )

        # Verify bindings were set up
        expected_bind_calls = [
            (sample_circle, "color", "color"),
            (sample_circle, "weight", "weight"),
            (sample_circle, "opacity", "opacity"),
            (sample_circle, "fill", "fill"),
            (sample_circle, "fill_color", "fill_color"),
            (sample_circle, "fill_opacity", "fill_opacity"),
        ]

        assert mock_circle.bind.call_count == 6
        for expected_call in expected_bind_calls:
            mock_circle.bind.assert_any_call(*expected_call)

        assert result == mock_circle


# Integration Tests
class TestMapConvertersIntegration:
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
            locations=locations,
        )

        # Convert to dict and back
        dict_result = polyline_converter.convert(polyline)
        reversed_polyline = polyline_converter.reverse_convert(dict_result)
        assert reversed_polyline == polyline

        # Test polygon
        polygon_converter = MapPolygonGridConverter()
        polygon_locations = [
            LatLng(37.7749, -122.4194),
            LatLng(37.7849, -122.4094),
            LatLng(37.7949, -122.3994),
            LatLng(37.7749, -122.4194),
        ]
        polygon = MapPolygon(
            shape_id="test_polygon",
            color="#00FF00",
            weight=2.0,
            opacity=0.7,
            locations=polygon_locations,
            fill=True,
            fill_color="#00FF00",
            fill_opacity=0.3,
        )

        # Convert to dict and back
        dict_result = polygon_converter.convert(polygon)
        reversed_polygon = polygon_converter.reverse_convert(dict_result)
        assert reversed_polygon == polygon

    @pytest.mark.parametrize(
        "converter_class,kwargs",
        [
            (MapPolylineMapConverter, {"some_param": "test"}),
            (MapPolygonMapConverter, {"another_param": 42}),
            (MapCircleMapConverter, {"test_kwarg": True}),
        ],
    )
    def test_converter_with_kwargs(self, converter_class, kwargs):
        """Test that converters handle keyword arguments properly."""
        converter = converter_class(**kwargs)
        assert isinstance(converter, converter_class)


# Parametrized Tests
class TestConverterEdgeCases:
    @pytest.mark.parametrize(
        "converter_class,none_result",
        [
            (MapPolylineGridConverter, {}),
            (MapPolygonGridConverter, {}),
        ],
    )
    def test_grid_converters_handle_none(self, converter_class, none_result):
        """Test that grid converters properly handle None inputs."""
        converter = converter_class()
        result = converter.convert(None)
        assert result == none_result

    @pytest.mark.parametrize(
        "converter_class",
        [
            MapPolylineGridConverter,
            MapPolygonGridConverter,
        ],
    )
    def test_reverse_convert_with_missing_keys(self, converter_class):
        """Test that reverse conversion raises KeyError for missing keys."""
        converter = converter_class()
        with pytest.raises(KeyError):
            converter.reverse_convert({"shape_id": "nonexistent"})
