from typing import Any, Dict, List, Mapping, Self
from dataclasses import dataclass, is_dataclass, asdict
from nicegui.elements.aggrid import AgGrid as NiceGUIAgGrid

from nicemvvm.observables.Observable import Observer, Observable, ObserverHandler
from nicemvvm.observables.ObservableCollections import ObservableList


@dataclass
class GridViewColumn:
    header: str
    field: str
    type: str|List[str]|None = None   # "rightAligned", "numericColumn"
    filter: bool = False
    sortable: bool = True
    selection: bool = False
    width: int|None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "headerName": self.header,
            "field": self.field,
            "type": self.type,
            "filter": self.filter,
            "sortable": self.sortable,
            "checkboxSelection": self.selection,
            "width": self.width,
        }


def to_dict(item: Any) -> Dict[str, Any]:
    if is_dataclass(item):
        return asdict(item)
    else:
        return item.__dict__


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
                "defaultColDef": {
                    "flex": 0
                },
                ":getRowId": ""
            }
        else:
            self._options = options

        super().__init__(
            options=self._options,
            auto_size_columns=True)

    def set_row_id(self, row_id: str) -> None:
        if len(row_id) == 0:
            self._options[":getRowId"] = ""
        else:
            self._options[":getRowId"] = f"(params) => params.data.{row_id}"
        self.update()

    def bind(self,
             source: Observable,
             property_name: str,
             local_name: str,
             handler: ObserverHandler | None = None) -> Self:

        Observer.bind(self, source, property_name, local_name, handler)
        if local_name == "items":
            self.update()
        return self

    @property
    def columns(self) -> List[GridViewColumn]:
        return self._columns

    @columns.setter
    def columns(self, columns: List[GridViewColumn]) -> None:
        self._columns = columns
        self._options["columnDefs"] = [c.to_dict() for c in columns]
        self.update()

    @property
    def items(self) -> List[Any]:
        return self._items

    @items.setter
    def items(self, items: List[Any]) -> None:
        self._items = items
        self._options["rowData"] = [to_dict(item) for item in items]

        if isinstance(items, ObservableList):
            source: ObservableList = items
            source.register(self._items_handler)

    def _items_handler(self, action: str, args: Mapping[str, Any]) -> None:
        self.update()