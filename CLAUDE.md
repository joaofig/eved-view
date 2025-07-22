# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- **Run application**: `make run` or `uv run evedview.py`
- **Setup project**: `make setup` (initializes uv project and syncs dependencies)
- **Code formatting**: `make format` (runs ruff format, fix, and import sorting)
- **Linting**: `make check` or `uvx ruff check .`

## Architecture Overview

This is a Python web application built with NiceGUI for viewing eVED (electric vehicle event data) datasets. The application follows an MVVM (Model-View-ViewModel) architecture pattern.

### Core Components

- **Application Entry**: `app/evedview.py` sets up the main NiceGUI page with dependency injection via ResourceLocator
- **MVVM Framework**: Custom `nicemvvm/` package provides MVVM infrastructure including:
  - Observable properties and collections
  - Command pattern implementation
  - Custom UI controls (buttons, inputs, leaflet map components)
  - Resource locator for dependency injection
- **Main UI**: Split-pane interface with trip data controls on left and interactive map on right
- **Map Integration**: Custom leaflet controls for displaying GPS traces, matches, and road network nodes

### Project Structure

- `app/`: Main application code following MVVM pattern
  - `models/`: Data models (TripModel)
  - `viewmodels/`: View models with business logic
  - `views/`: UI views and editors
  - `commands/`: Command pattern implementations
  - `converters/`: Data converters for UI binding
  - `repositories/`: Data access layer
  - `geo/`: Geographic computation utilities
- `nicemvvm/`: Custom MVVM framework built on top of NiceGUI
- `tools/`: Utility modules (config, database helpers)

### Key Technologies

- **NiceGUI**: Web UI framework based on FastAPI
- **UV**: Python package manager and project runner
- **Ruff**: Code formatting and linting
- **Dependencies**: numpy, pandas, shapely for data processing

### Development Notes

- The application uses a custom dependency injection system via ResourceLocator singleton
- Map functionality is built with custom leaflet controls that extend NiceGUI
- The codebase follows a clean separation of concerns with MVVM pattern
- All UI components are built using the custom `nicemvvm` framework