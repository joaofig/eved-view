from nicegui import ui, events
from src.controls.LeafletMap import LeafletMap
from src.message.Messenger import Messenger, AppMsg
from src.ui.models.map import MapModel
from src.ui.models.trip import TripList, TripDisplay
from src.ui.services.trip import get_noisy_trajectory
from src.ui.viewmodels.MapViewModel import MapViewModel


class MapView:
    def __init__(self, view_model: MapViewModel):
        self.m: LeafletMap
        self.view_model = view_model

        messenger = Messenger()

        options = {
            "maxZoom": 22,
        }
        draw_control = {
            "draw": {
                "polygon": True,
                "marker": False,
                "circle": False,
                "rectangle": False,
                "polyline": False,
                "circlemarker": False,
            },
            "edit": {
                "edit": True,
                "remove": True,
            },
        }

        with ui.row().classes("w-full h-full"):
            self.m = LeafletMap(
                zoom=3,
                draw_control=draw_control,
                options=options,  # , classes="h-full w-full"
            )
        with ui.row():
            self.center_btn = (
                ui.button(icon="crop_free")
                .tooltip("Center map")
                # .classes("mt-0")
                .on_click(self.on_center_map_clicked)
            )
            self.clear_btn = (
                ui.button(icon="clear")
                .tooltip("Clear map")
                # .classes("mt-0")
                .on_click(self.on_clear_map_clicked)
            )

        messenger.subscribe("map", "show_trip", self.on_show_trip)
        messenger.subscribe("map", "hide_trip", self.on_hide_trip)

    async def on_show_trip(self, msg: AppMsg) -> None:
        ui.notify(msg.data)

        trip_display: TripDisplay = msg.data
        if trip_display.type == "gps":
            pass

            # if self.model.has_gps_trip(trip_display.traj_id):
            #     pass
            #
            # traj = get_noisy_trajectory(trip_display.traj_id)
            # # polyline: PolylineModel = PolylineModel(traj)
            # polyline = self.m.polyline(traj)

    async def on_hide_trip(self, msg: AppMsg) -> None:
        trip_display: TripDisplay = msg.data

    def on_center_map_clicked(self, e: events.ClickEventArguments) -> None:
        ui.notify("Center Map!")

    def on_clear_map_clicked(self, e: events.ClickEventArguments) -> None:
        ui.notify("Clear Map!")
