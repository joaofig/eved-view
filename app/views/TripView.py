
from nicegui.elements.column import Column
from nicemvvm.controls.GridView import GridView, GridViewColumn



class TripView(Column):
    def __init__(self):
        super().__init__()

        self._grid = GridView()
        self._grid.columns = [
            GridViewColumn(header="Trip", field="traj_id", filter=True),
            GridViewColumn(header="Vehicle", field="vehicle_id", filter=True),
            GridViewColumn(header="Start", field="dt_ini", filter=True),
            GridViewColumn(header="End", field="dt_end", filter=True),
        ]
