import json
from typing import List, Dict

import pandas as pd

from nicegui import ui, events
from src.db.EvedDb import EvedDb
from src.controls.GridView import GridView
from src.views.dialogs.TripSelectDialog import select_trips
from src.message.Messenger import Messenger, AppMsg
from src.models.trip import TripList, TripDisplay
from src.viewmodels.MapViewModel import MapViewModel
from src.viewmodels.TripSelectViewModel import TripSelectViewModel


def get_trips() -> pd.DataFrame:
    db = EvedDb()
    return db.get_trajectories()


COLUMN_DEFS = [
    {
        "headerName": "Trip",
        "field": "traj_id",
        "filter": True,
        # "headerCheckboxSelection": True,
        # "checkboxSelection": True,
    },
    {"headerName": "Vehicle", "field": "vehicle_id", "filter": True},
    {
        "headerName": "km",
        "field": "km",
        "filter": True,
        "type": "rightAligned",
    },
    {
        "headerName": "Noisy",
        "field": "view_noisy",
        "cellEditor": "agCheckboxCellEditor",
        "editable": True,
    },
    {
        "headerName": "Match",
        "field": "view_match",
        "cellEditor": "agCheckboxCellEditor",
        "editable": True,
    },
    {
        "headerName": "Graph",
        "field": "view_graph",
        "cellEditor": "agCheckboxCellEditor",
        "editable": True,
    },
]


def trip_selection_to_dict(vm: TripSelectionViewModel) -> Dict:
    return {
        "traj_id": vm.traj_id,
        "vehicle_id": vm.vehicle_id,
        "km": f"{vm.length_m / 1000:.2f}",
        "view_noisy": vm.view_noisy,
        "view_match": vm.view_match,
        "view_graph": vm.view_graph,
    }


class TripSelector:
    def __init__(self, view_model: MapViewModel):
        self.trips = dict()
        self.messenger = Messenger()
        self.view_model = view_model
        self._rows = []

        with ui.column().classes("w-full items-start"):
            # options = {
            #     "columnDefs": COLUMN_DEFS,
            #     "rowData": self._rows,
            #     "rowSelection": "single",
            #     "loading": False,
            # }
            self._grid_view = GridView(column_defs=COLUMN_DEFS)
            self._grid_view.bind(view_model.trips)
            # self.grid = ui.aggrid(options=options)
            # self.grid.on("rowSelected", lambda e: self.on_row_selected(e))
            # self.grid.on("cellValueChanged", self.on_cell_value_changed)

            with ui.row():
                self.open_btn = (
                    ui.button(icon="file_open")
                    .tooltip("Open trip")
                    .on_click(lambda e: self.on_open_trip(e))
                )
                # self.gps_btn = (
                #     ui.button(icon="location_disabled")
                #     .tooltip("Show noisy GPS trip locations")
                #     .on_click(self.show_noisy_gps_trips_clicked)
                # )
                # self.match_btn = (
                #     ui.button(icon="my_location")
                #     .tooltip("Show map-matched trip locations")
                #     .on_click(self.show_map_matched_trips_clicked)
                #     # .on_click(self.on_clear_clicked)
                # )
                # self.node_btn = (
                #     ui.button(icon="polyline")
                #     .tooltip("Show map-matched trip nodes")
                # )

        self.messenger.subscribe(
            "vehicle", "filter", lambda msg: self.on_filter_vehicles(msg)
        )

    async def on_cell_value_changed(self, e: events.GenericEventArguments) -> None:
        column = e.args["colId"]
        value = e.args["value"]
        trip = e.args["data"]
        traj_id = trip["traj_id"]
        trip_display = TripDisplay(trip["trip_id"], column)
        msg_name = "show_trip" if value else "hide_trip"
        await self.messenger.send("map", msg_name, trip_display)

    async def on_open_trip(self, _: events.ClickEventArguments) -> None:
        trips = await select_trips()
        if trips is None:
            return

        for trip in trips:
            traj_id = trip["traj_id"]
            if traj_id not in self.trips:
                trip_vm = TripSelectionViewModel(
                    traj_id=traj_id,
                    vehicle_id=trip["vehicle_id"],
                    length_m=trip["length_m"],
                    duration_s=trip["duration_s"],
                    dt_ini=trip["dt_ini"],
                    dt_end=trip["dt_end"],
                )
                await trip_vm.load_trajectories()
                # self.view_model.add_trip(trip_vm)
                # self._rows.append(trip_selection_to_dict(trip_vm))
                # self.trips[traj_id] = trip

        # self._grid_view.update()

        # data = list(self.trips.values())
        # await self.grid.run_grid_method("setGridOption",
        #                                 "rowData",
        #                                 self._rows)

    def on_center_map_clicked(self, _: events.ClickEventArguments) -> None:
        self.messenger.broadcast("map", AppMsg("center_map"))

    def on_clear_clicked(self, event: events.ClickEventArguments) -> None:
        pass

    #
    # def filter_grid(self, vehicles: List[int]):
    #     if len(vehicles) == 0:
    #         df = self.trips_df
    #     else:
    #         df = self.trips_df[self.trips_df["vehicle_id"].isin(vehicles)]
    #     rows = df.to_dict(orient="records")
    #     self.grid.run_grid_method("setGridOption", "rowData", rows)

    async def on_filter_vehicles(self, msg: AppMsg) -> None:
        # self.filter_grid(msg.data)
        pass

    def on_row_selected(self, event: events.GenericEventArguments) -> None:
        # selected = event.args["selected"]
        traj_id = event.args["data"]["traj_id"]
        self.view_model.selected_traj_id = traj_id

    def show_noisy_gps_trips_clicked(self, _: events.ClickEventArguments) -> None:
        pass
        # self.messenger.broadcast(
        #     "map", AppMsg("show_trips", TripList(list(self.selected_trips), "gps"))
        # )

    def show_map_matched_trips_clicked(self, _: events.ClickEventArguments) -> None:
        pass
        # self.messenger.broadcast(
        #     "map", AppMsg("show_trips", TripList(list(self.selected_trips), "match"))
        # )

    def show_map_node_trips_clicked(self, _: events.ClickEventArguments) -> None:
        pass
        # self.messenger.broadcast(
        #     "map", AppMsg("show_trips", TripList(list(self.selected_trips), "node"))
        # )
