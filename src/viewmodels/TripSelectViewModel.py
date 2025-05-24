from src.db.EvedDb import EvedDb
from typing import List
from src.viewmodels.BaseViewModel import BaseViewModel


class TripSelectViewModel(BaseViewModel):
    def __init__(self):
        super().__init__()
        db = EvedDb()
        df = db.get_trajectories()
        self._trips = df[["trip_id", "vehicle_id", "km"]].to_dict("records")

    @property
    def trips(self) -> List:
        return self._trips
