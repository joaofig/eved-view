from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from app.models.MapNode import MapNode
from app.models.Signal import Signal
from app.repositories.trip import load_signals, load_nodes


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
        self.signals = load_signals(self.traj_id)

    def load_nodes(self) -> None:
        """
        Load map nodes for this trip.
        """
        self.nodes = load_nodes(self.traj_id)
