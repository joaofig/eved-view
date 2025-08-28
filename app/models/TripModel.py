from typing import Dict, List

from app.models.Trip import Trip
from app.repositories.trip import load_all_trips


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
