from dataclasses import dataclass


@dataclass
class Signal:
    signal_id: int
    day_num: float
    timestamp: int
    vehicle_id: int
    trip_id: int
    lat: float
    lon: float
    match_lat: float
    match_lon: float
    speed: float
    elevation: float
    elevation_smooth: float
    gradient: float | None
    h3_12: int
