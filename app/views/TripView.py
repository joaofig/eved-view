from nicegui import ui

from nicemvvm import nm
from nicemvvm.observables.Observable import Observable


class TripView(ui.column):
    def __init__(self, view_model: Observable):
        super().__init__()

        self._grid = (nm.gridview()
                        .bind(view_model, property_name="trips", local_name="items")
                        .bind(view_model, property_name="selected_trip", local_name="selected_item")
        )
        self._grid.columns = [
            nm.gridview_col(header="Trip", field="traj_id", filter=True, width=70),
            nm.gridview_col(
                header="Vehicle", field="vehicle_id", filter=True, width=75
            ),
            nm.gridview_col(header="km", field="km", filter=True, width=60),
            nm.gridview_col(header="Start", field="start", filter=True, width=100),
            nm.gridview_col(header="End", field="end", filter=True),
        ]
        self._grid.row_id = "traj_id"
