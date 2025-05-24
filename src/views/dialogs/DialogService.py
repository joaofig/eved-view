from nicegui import ui
from src.views.dialogs.TripSelectDialog import TripSelectDialog
from src.message.Messenger import Messenger, AppMsg
from src.viewmodels.MapViewModel import MapViewModel


class DialogService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DialogService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        messenger = Messenger()

        messenger.subscribe(
            channel="dialog", name="select_trips", handler=self.on_select_trips
        )

    async def on_select_trips(self, message: AppMsg) -> None:
        if message.data is MapViewModel:
            view_model: MapViewModel = message.data
            trip_select = TripSelectDialog()
            trips = await trip_select.dialog
            trip_select.dialog.clear()
        else:
            ui.notify("message.data is not a MapViewModel")
