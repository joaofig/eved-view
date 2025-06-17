
from nicegui.elements.column import Column
from nicemvvm.controls.GridView import GridView, GridViewColumn
from nicemvvm.observables.Observable import Observable


class TripView(Column):
    def __init__(self, view_model: Observable):
        super().__init__()

        self._grid = GridView() \
            .bind(view_model, "trips", "items") \
            .bind(view_model, "selected_trip", "selected_item")
        self._grid.columns = [
            GridViewColumn(header="Trip", field="traj_id", filter=True, width=70),
            GridViewColumn(header="Vehicle", field="vehicle_id", filter=True, width=75),
            GridViewColumn(header="km", field="km", filter=True, width=60),
            GridViewColumn(header="Start", field="start", filter=True, width=100),
            GridViewColumn(header="End", field="end", filter=True),
        ]
        self._grid.row_id = "traj_id"