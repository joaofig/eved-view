from src.message.Observable import ObservableList
from src.viewmodels.BaseViewModel import BaseViewModel


class MapViewModel(BaseViewModel):
    def __init__(self):
        super().__init__()
        self._trips = ObservableList()

    @property
    def trips(self) -> ObservableList:
        return self._trips
