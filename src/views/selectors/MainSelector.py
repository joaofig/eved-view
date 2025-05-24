from nicegui import ui

from src.message.Messenger import Messenger
from src.views.selectors.TripSelector import TripSelector
from src.views.selectors.VehicleSelector import VehicleSelector
from src.views.dialogs.TripSelectDialog import select_trips
from src.viewmodels.MapViewModel import MapViewModel


#
# async def on_select_trips(messenger: Messenger) -> None:
#     trips = await select_trips()
#     ui.notify(trips)


class MainSelector:
    def __init__(self, view_model: MapViewModel) -> None:
        # with ui.expansion(text="Vehicles", icon="directions_car").classes("w-full"):
        #     vehicles = VehicleSelector(messenger)

        with ui.expansion(text="Trips", icon="route").classes("w-full"):
            TripSelector(view_model)

        with ui.expansion(text="Geofence", icon="pentagon").classes("w-full"):
            ui.label("Geofence")

        with ui.expansion(text="Settings", icon="settings").classes("w-full"):
            ui.label("Settings")
