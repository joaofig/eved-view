from typing import Any, Dict, List, Mapping
from dataclasses import dataclass
from nicegui.elements.aggrid import AgGrid as NiceGUIAgGrid

from nicemvvm.observables.Observable import Observer
from nicemvvm.observables.ObservableCollections import ObservableList


@dataclass
class GridViewColumn:
    header: str
    field: str
    type: str|List[str]|None = None   # "rightAligned", "numericColumn"
    filter: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "headerName": self.header,
            "field": self.field,
            "type": self.type,
            "filter": self.filter
        }


class GridView(NiceGUIAgGrid, Observer):
    def __init__(self, options: Dict|None = None):
        self._columns: List[GridViewColumn] = []
        self._items: List[Dict] = []

        if options is None:
            self._options = {
                "columnDefs": [],
                "rowData": [],
                "rowSelection": "single",
                "loading": False,
            }
        else:
            self._options = options

        super().__init__(
            options=self._options,
            auto_size_columns=True)

    @property
    def columns(self) -> List[GridViewColumn]:
        return self._columns

    @columns.setter
    def columns(self, columns: List[GridViewColumn]) -> None:
        self._columns = columns
        self._options["columnDefs"] = [c.to_dict() for c in columns]
        self.update()

    @property
    def items(self) -> List[Dict]:
        return self._items

    @items.setter
    def items(self, items: List[Dict]) -> None:
        self._items = items
        self._options["rowData"] = items

        if isinstance(items, ObservableList):
            source: ObservableList = items
            source.register(self._items_handler)

    def _items_handler(self, action: str, args: Mapping[str, Any]) -> None:
        self.update()