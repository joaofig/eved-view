import asyncio
from typing import Any, Dict, List, Mapping, Self
from dataclasses import dataclass, is_dataclass, asdict
from nicegui import events
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
        self._items: List[Any] = []
        self._selected_item: Any|None = None
        self._row_id: str = ""

        if options is None:
            self._options = {
                "columnDefs": [],
                "rowData": [],
                "rowSelection": "single",
                "loading": False,
                "defaultColDef": {
                    "flex": 0
                },
                # ":getRowId": ""
            }
        else:
            self._options = options

        super().__init__(
            options=self._options,
            auto_size_columns=True)

    def bind(self,
             source: Observable,
             property_name: str,
             local_name: str,
             handler: ObserverHandler | None = None) -> Self:

        if local_name == "selected_item":
            self.on('selectionChanged', self._selection_changed_handler)

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

    async def _find_selected_row(self, column: str) -> None:
        row = await self.get_selected_row()
        for item in self._items:
            if getattr(item, column) == row[column]:
                self._selected_item = item
                self._outbound_handler("selected_item", item)
                break

    def _selection_changed_handler(self, event: events.GenericEventArguments) -> None:
        if event.args["source"] == "rowClicked":
            column = self._row_id
            if len(column) > 0:
                asyncio.create_task(self._find_selected_row(column))

    def _items_handler(self, action: str, args: Mapping[str, Any]) -> None:
        self.update()

    def _set_row_id(self, row_id: str) -> None:
        if len(row_id) == 0:
            del self._options[":getRowId"]
        else:
            self._options[":getRowId"] = f"(params) => String(params.data.{row_id})"
        self.update()

    @property
    def row_id(self) -> str:
        return self._row_id

    @row_id.setter
    def row_id(self, row_id: str) -> None:
        self._set_row_id(row_id)
        self._row_id = row_id

    async def _select_item(self, item: Any) -> None:
        column = self._row_id
        if len(column) > 0:
            row_id_value = str(getattr(item, column))
            row = await self.run_grid_method("getRowNode", row_id_value)
            if row is not None:
                await self.run_row_method(row, "setSelected", True)

    @property
    def selected_item(self) -> Any|None:
        return self._selected_item

    @selected_item.setter
    def selected_item(self, item: Any|None) -> None:
        if self._selected_item != item:
            self._selected_item = item
            asyncio.create_task(self._select_item(item))
