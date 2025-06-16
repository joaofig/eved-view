
from nicegui.elements.column import Column
from nicemvvm.controls.GridView import GridView, GridViewColumn
from nicemvvm.observables.Observable import Observable


class TripView(Column):
    def __init__(self, view_model: Observable):
        super().__init__()

        self._grid = GridView().bind(view_model, "trips", "items")
        self._grid.columns = [
            GridViewColumn(header="Trip", field="traj_id", filter=True),
            GridViewColumn(header="Vehicle", field="vehicle_id", filter=True),
            GridViewColumn(header="km", field="km", filter=True),
            GridViewColumn(header="Start", field="start", filter=True),
            GridViewColumn(header="End", field="end", filter=True),
        ]
