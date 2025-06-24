from dataclasses import dataclass
from typing import List

# from src.db.EvedDb import EvedDb


@dataclass
class Location:
    lat: float
    lon: float


@dataclass
class TripGeometry:
    points: List[Location]
    color: str = "blue"
    opacity: float = 1.0


@dataclass
class VehicleTrip:
    # The following fields originate in the trajectory table
    traj_id: int
    vehicle_id: int
    trip_id: int
    length_m: float
    duration_s: float

    dt_ini: str
    dt_end: str

    # The trip information originates in the signal and node tables
    noisy_trip: TripGeometry
    match_trip: TripGeometry
    graph_trip: TripGeometry

    # These indicators affect the UI
    show_noisy: bool = False
    show_match: bool = False
    show_graph: bool = False


class MapModel:
    def __init__(self):
        self.trips: List[VehicleTrip] = []

    # def load_trajectory(self, traj_id) -> None:
    #     base_db = EvedDb()
    #     traj_df = base_db.get_trajectory(traj_id)
