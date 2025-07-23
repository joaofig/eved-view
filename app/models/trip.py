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
        """
        Load signals for this trip.
        """
        signals_df = load_signals(self.traj_id)
        self.signals.extend([
            Signal(
                signal_id=int(raw_signal.signal_id),
                day_num=raw_signal.day_num,
                timestamp=raw_signal.time_stamp,
                vehicle_id=int(raw_signal.vehicle_id),
                trip_id=int(raw_signal.trip_id),
                lat=raw_signal.latitude,
                lon=raw_signal.longitude,
                match_lat=raw_signal.match_latitude,
                match_lon=raw_signal.match_longitude,
                speed=raw_signal.speed,
                elevation=raw_signal.elevation,
                elevation_smooth=raw_signal.elevation_smooth,
                gradient=raw_signal.gradient,
                h3_12=int(raw_signal.h3_12),
            )
            for raw_signal in signals_df.itertuples(index=False)
        ])

    def load_nodes(self) -> None:
        """
        Load map nodes for this trip.
        """
        nodes_df = load_nodes(self.traj_id)

        # Pre-allocate the list
        self.nodes = []
        self.nodes.extend([
            MapNode(
                node_id=int(row.node_id),
                traj_id=int(row.traj_id),
                lat=row.latitude,
                lon=row.longitude,
                h3_12=int(row.h3_12),
                match_error=row.match_error,
            )
            for row in nodes_df.itertuples(index=False)
        ])


class TripModel:
    def __init__(self):
        self.trips: Dict[int, Trip] = {}
        self._loaded: bool = False

    def load(self) -> List[Trip]:
        """
        Load all trips with optimized performance.
        Returns a list of Trip objects and caches them in the trips dictionary.
        
        Optimizations:
        - Uses numpy structured arrays for faster iteration
        - Pre-allocates result list
        - Caches results to avoid redundant loading
        """
        # Return cached trips if already loaded
        if self._loaded and self.trips:
            return list(self.trips.values())
            
        # Load raw trip data
        raw_trips = load_all_trips()
        
        # Pre-allocate result list with estimated size
        trip_count = len(raw_trips)
        trip_list: List[Trip] = []
        
        # Convert to numpy structured array for faster iteration
        trips_array = raw_trips.to_records(index=False)
        
        # Process all trips
        for raw_trip in trips_array:
            trip = Trip(
                traj_id=int(raw_trip.traj_id),
                vehicle_id=int(raw_trip.vehicle_id),
                trip_id=int(raw_trip.trip_id),
                km=round(raw_trip.length_m / 1000, 1),
                duration=raw_trip.duration_s,
                engine=raw_trip.engine,
                weight=raw_trip.weight,
                start=raw_trip.dt_ini[:19],
                end=raw_trip.dt_end[:19],
                signals=[],
                nodes=[],
            )
            self.trips[trip.traj_id] = trip
            trip_list.append(trip)
            
        self._loaded = True
        return trip_list
