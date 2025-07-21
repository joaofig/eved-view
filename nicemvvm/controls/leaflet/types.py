from dataclasses import dataclass
from enum import Enum


@dataclass
class LatLng:
    lat: float
    lng: float
    alt: float = 0.0

    def to_list(self) -> list[float]:
        return [self.lat, self.lng]

    def to_dict(self) -> dict:
        return {"lat": self.lat, "lng": self.lng}


class ControlPosition(Enum):
    TOPLEFT = "topleft"
    TOPRIGHT = "topright"
    BOTTOMLEFT = "bottomleft"
    BOTTOMRIGHT = "bottomright"
