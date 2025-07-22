import asyncio
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Dict, List, Mapping, Self

from nicegui import events
from nicegui.elements.aggrid import AgGrid as NiceGUIAgGrid

from nicemvvm.converter import ValueConverter
from nicemvvm.observables.collections import ObservableList
from nicemvvm.observables.observability import (
    Observable,
    Observer,
    ObserverHandler,
)


@dataclass
class GridViewColumn:
    header: str
    field: str
    type: str | List[str] | None = None  # "rightAligned", "numericColumn"
    filter: bool = False
    sortable: bool = True
    selection: bool = False
    width: int | None = None

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
    def __init__(
        self,
        row_selection: str = "single",
        supress_auto_size: bool = False,
        options: Dict | None = None,
    ):
        self._columns: List[GridViewColumn] = []
        self._items: List[Dict[str, Any]] = []
        self._selected_item: Any | None = None
        self._selected_items: List[Dict[str, Any]] = []
        self._row_id: str = ""
        self._item_converter: ValueConverter | None = None

        self._options = {
            "columnDefs": [],
            "rowData": self._items,
            "rowSelection": row_selection,
            "loading": False,
            "suppressAutoSize": supress_auto_size,
        }
        if options:
            self._options.update(options)

        super().__init__(options=self._options, auto_size_columns=True)

    def _item_list_handler(self, action: str, args: Dict[str, Any]) -> None:
        converter = self._item_converter

        match action:
            case "append" | "iadd":
                item = args["value"]
                if converter is not None:
                    item = converter.convert(item)
                self._items.append(item)

            case "extend":
                values = args["values"]
                self._items.extend(
                    [
                        item if converter is None else converter.convert(item)
                        for item in values
                    ]
                )

            case "insert":
                item = args["value"]
                index = args["index"]
                self._items.insert(
                    index, item if converter is None else converter.convert(item)
                )

            case "remove" | "pop":
                item = args["value"]
                index = args["index"]
                self._items.remove(self._items[index])

            case "clear":
                self._items.clear()

            case "set_slice":
                new_values = args["new_values"]
                list_slice = args["slice"]
                self._items[list_slice] = [
                    item if converter is None else converter.convert(item)
                    for item in new_values
                ]

            case "set_item":
                new_value = args["new_value"]
                index = args["index"]
                self._items[index] = (
                    new_value if converter is None else converter.convert(new_value)
                )

        self.update()

    def bind(
        self,
        source: Observable,
        property_name: str,
        local_name: str,
        handler: ObserverHandler | None = None,
        converter: ValueConverter | None = None,
    ) -> Self:
        match local_name:
            case "selected_item":
                self.on("selectionChanged", self._selection_changed_handler)
                Observer.bind(
                    self, source, property_name, local_name, handler, converter
                )

            case "items":
                items = getattr(source, property_name)
                if isinstance(items, ObservableList):
                    obs_list: ObservableList = items
                    obs_list.register(self._item_list_handler)
                self._item_converter = converter
                self._items.extend(
                    [
                        item if converter is None else converter.convert(item)
                        for item in items
                    ]
                )
                self.update()

            case _:
                raise ValueError(f"GridView.bind - Invalid local name: {local_name}")

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
    def items(self) -> List[Dict[str, Any]]:
        return self._items

    @items.setter
    def items(self, items: List[Dict[str, Any]]) -> None:
        self._items = items
        self._options["rowData"] = items

        if isinstance(items, ObservableList):
            source: ObservableList = items
            source.register(self._items_handler)

    async def _find_selected_row(self, column: str) -> None:
        row = await self.get_selected_row()
        for item in self._items:
            if item[column] == row[column]:
                self._selected_item = item
                self._outbound_handler("selected_item", item)
                break

    async def _find_selected_rows(self, column: str) -> None:
        identifiers = set(r[column] for r in await self.get_selected_rows())
        selected_items = []
        count = 0
        for item in self._items:
            value = item[column]
            if value in identifiers:
                selected_items.append(item)
                count += 1
        if count:
            self._outbound_handler("selected_items", selected_items)

    def _selection_changed_handler(self, event: events.GenericEventArguments) -> None:
        if event.args["source"] == "rowClicked":
            column = self._row_id
            if column:
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

    def _select_item(self, item: Dict[str, Any]) -> None:
        column = self._row_id
        if len(column) > 0 and item and column in item:
            row_id_value = str(item[column])
            self.run_row_method(row_id_value, "setSelected", True)

    async def _select_items(self, items: List[Any]) -> None:
        column = self._row_id
        if column:
            for item in items:
                row_id_value = str(getattr(item, column))
                await self.run_row_method(row_id_value, "setSelected", True)

    @property
    def selected_item(self) -> Any | None:
        return self._selected_item

    @selected_item.setter
    def selected_item(self, item: Any | None) -> None:
        if self._selected_item != item:
            self._selected_item = item
            self._select_item(item)
            # asyncio.create_task(self._select_item(item))

    @property
    def selected_items(self) -> List[Any] | None:
        return self._selected_items

    @selected_items.setter
    def selected_items(self, items: List[Any] | None) -> None:
        if self._selected_items != items:
            self._selected_items = items
            asyncio.create_task(self._select_items(items))
