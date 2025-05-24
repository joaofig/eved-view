from nicegui import ui, events
from typing import Dict, List
from src.viewmodels.TripSelectViewModel import TripSelectViewModel


COLUMN_DEFS = [
    {
        "headerName": "Trip",
        "field": "trip_id",
        "filter": True,
        # "headerCheckboxSelection": True,
        "checkboxSelection": True,
    },
    {
        "headerName": "Vehicle",
        "field": "vehicle_id",
        "filter": True,
    },
    {
        "headerName": "km",
        "field": "km",
    },
]


class TripSelectDialog:
    def __init__(self):
        self.view_model = TripSelectViewModel()
        with ui.dialog() as dialog, ui.card():
            self.dialog = dialog

            options = {
                "columnDefs": COLUMN_DEFS,
                "rowData": self.view_model.trips,
                "rowSelection": "multiple",
            }

            self.grid = ui.aggrid(options=options).classes(
                "w-[400px]"
            )

            with ui.row().classes("w-full"):
                ui.button(text="Select", on_click=self.on_select_trips)
                ui.space()
                ui.button(text="Close", on_click=lambda e: dialog.submit([]))

    async def on_select_trips(self):
        rows = await self.grid.get_selected_rows()
        # ui.notify(f"Selected {len(rows)} trips")
        # ui.notify(rows)
        self.dialog.submit(rows)


async def select_trips() -> List[Dict]:
    trip_select = TripSelectDialog()
    trips = await trip_select.dialog
    trip_select.dialog.clear()
    return trips
