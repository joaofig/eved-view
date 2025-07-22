# eVED Viewer

A modern web-based viewer for exploring and visualizing eVED (electric Vehicle Event Data) datasets. Built with Python and NiceGUI, this application provides an interactive interface for analyzing GPS traces, map-matched routes, and road network data.

## Features

- **Interactive Map Visualization**: View GPS traces, map-matched routes, and road network nodes on an interactive leaflet map
- **Trip Data Management**: Load and manage trip data with an intuitive interface
- **MVVM Architecture**: Clean separation of concerns using a custom MVVM framework built on NiceGUI
- **Real-time Updates**: Observable properties and reactive UI components for seamless data interaction
- **Modular Design**: Extensible architecture with custom controls and components

## Prerequisites

- Python 3.13 or higher
- [UV](https://docs.astral.sh/uv/) package manager

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/joaofig/eved-view.git
   cd eved-view
   ```

2. **Set up the development environment**:
   ```bash
   make setup
   ```

3. **Run the application**:
   ```bash
   make run
   ```

4. **Open your browser** and navigate to `http://localhost:8080`

## Development

### Available Commands

- `make run` - Start the application
- `make setup` - Initialize the project and install dependencies
- `make format` - Format code with ruff (includes import sorting)
- `make check` - Run linting checks

### Testing

The project includes comprehensive unit tests for core components:

- **Map Converters**: Tests for all map converter classes located in `tests/test_map_converters.py`
  - `MapPolylineGridConverter` - Grid data conversion for polylines
  - `MapPolygonGridConverter` - Grid data conversion for polygons  
  - `MapPolylineMapConverter` - Map control conversion for polylines
  - `MapPolygonMapConverter` - Map control conversion for polygons
  - `MapCircleMapConverter` - Map control conversion for circles

Run tests using:
```bash
python -m pytest tests/
# or
python -m unittest discover tests/
```

### Project Structure

```
eved-view/
├── app/                    # Main application code
│   ├── commands/          # Command pattern implementations
│   ├── converters/        # Data converters for UI binding
│   ├── geo/              # Geographic computation utilities
│   ├── models/           # Data models
│   ├── repositories/     # Data access layer
│   ├── services/         # Business services
│   ├── viewmodels/       # MVVM view models
│   └── views/            # UI views and editors
├── nicemvvm/              # Custom MVVM framework
│   ├── controls/         # Custom UI controls
│   │   └── leaflet/     # Leaflet map components
│   └── observables/     # Observable properties system
└── tools/                # Utility modules
    └── database/         # Database helpers
```

### Architecture

The application follows the MVVM (Model-View-ViewModel) pattern:

- **Models**: Data structures representing trips, GPS points, and geographic features
- **ViewModels**: Business logic and state management with observable properties
- **Views**: UI components built with NiceGUI and custom controls
- **Commands**: Action handlers following the command pattern

### Key Technologies

- **[NiceGUI](https://nicegui.io/)**: Modern web UI framework for Python
- **[UV](https://docs.astral.sh/uv/)**: Fast Python package installer and resolver
- **[Ruff](https://docs.astral.sh/ruff/)**: Extremely fast Python linter and formatter
- **NumPy & Pandas**: Data processing and analysis
- **Shapely**: Geometric operations and spatial analysis

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and ensure they follow the coding standards
4. Run `make format` and `make check` to ensure code quality
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the terms specified in the LICENSE file.
