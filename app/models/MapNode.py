from dataclasses import dataclass


@dataclass
class MapNode:
    node_id: int
    traj_id: int
    lat: float
    lon: float
    h3_12: int
    match_error: str | None = None
