from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

from app.repositories.trip import load_all_trips, load_nodes, load_signals


@dataclass
class MapNode:
    node_id: int
    traj_id: int
    lat: float
    lon: float
    h3_12: int
    match_error: str | None = None


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
    gradient: float
    h3_12: int


@dataclass
class Trip:
    traj_id: int
    vehicle_id: int
    trip_id: int
    km: float
    duration: float
    engine: str
    weight: float
    start: datetime
    end: datetime
    signals: List[Signal] = field(default_factory=list)
    nodes: List[MapNode] = field(default_factory=list)

    def load_signals(self) -> None:
        signals = load_signals(self.traj_id)
        self.signals = [
            Signal(
                signal_id=raw_signal.signal_id,
                day_num=raw_signal.day_num,
                timestamp=raw_signal.time_stamp,
                vehicle_id=raw_signal.vehicle_id,
                trip_id=raw_signal.trip_id,
                lat=raw_signal.latitude,
                lon=raw_signal.longitude,
                match_lat=raw_signal.match_latitude,
                match_lon=raw_signal.match_longitude,
                speed=raw_signal.speed,
                elevation=raw_signal.elevation,
                elevation_smooth=raw_signal.elevation_smooth,
                gradient=raw_signal.gradient,
                h3_12=raw_signal.h3_12,
            )
            for raw_signal in signals.itertuples(index=False)
        ]

    def load_nodes(self) -> None:
        nodes = load_nodes(self.traj_id)
        self.nodes = [
            MapNode(
                node_id=raw_node.node_id,
                traj_id=raw_node.traj_id,
                lat=raw_node.latitude,
                lon=raw_node.longitude,
                h3_12=raw_node.h3_12,
                match_error=raw_node.match_error,
            )
            for raw_node in nodes.itertuples(index=False)
        ]


class TripModel:
    def __init__(self):
        self.trips: Dict[int, Trip] = {}

    def load(self) -> List[Trip]:
        raw_trips = load_all_trips()
        trip_list: List[Trip] = []
        for raw_trip in raw_trips.itertuples(index=False):
            trip = Trip(
                traj_id=raw_trip.traj_id,
                vehicle_id=raw_trip.vehicle_id,
                trip_id=raw_trip.trip_id,
                km=round(raw_trip.length_m / 1000, 1),
                duration=raw_trip.duration_s,
                engine=raw_trip.engine,
                weight=raw_trip.weight,
                start=raw_trip.dt_ini[:19],
                end=raw_trip.dt_end[:19],
                signals=[],
            )
            self.trips[trip.traj_id] = trip
            trip_list.append(trip)
        return trip_list

    def __getitem__(self, traj_id: int) -> Trip:
        return self.trips[traj_id]
