from dataclasses import dataclass
from enum import Enum
from typing import List


@dataclass
class LatLng:
    lat: float
    lng: float
    alt: float = 0.0

    def to_list(self) -> List[float]:
        return [self.lat, self.lng]


class ControlPosition(Enum):
    TOPLEFT = "topleft"
    TOPRIGHT = "topright"
    BOTTOMLEFT = "bottomleft"
    BOTTOMRIGHT = "bottomright"
