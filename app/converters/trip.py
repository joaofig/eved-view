from typing import Dict

from app.models.TripModel import Trip
from nicemvvm.converter import ValueConverter


class TripToDictConverter(ValueConverter):
    def __init__(self):
        super().__init__()

    def convert(self, trip: Trip) -> Dict:
        if trip:
            return trip.__dict__ | {"_source": trip}
        else:
            return {"_source": None}

    def reverse_convert(self, value: Dict) -> Trip:
        return value["_source"]
