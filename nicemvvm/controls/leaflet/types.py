from dataclasses import dataclass
from enum import Enum
from typing import Self


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


@dataclass
class GeoBounds:
    sw: LatLng
    ne: LatLng

    def merge(self, other: Self) -> Self:
        return GeoBounds(
            sw=LatLng(
                min(self.sw.lat, other.sw.lat),
                min(self.sw.lng, other.sw.lng)
            ),
            ne=LatLng(
                max(self.ne.lat, other.ne.lat),
                max(self.ne.lng, other.ne.lng)
            )
        )
