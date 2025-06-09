from typing import Any, Dict, List
from dataclasses import dataclass
from nicegui.elements.aggrid import AgGrid as NiceGUIAgGrid

from nicemvvm.Observable import Observable, Observer


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
            options=options,
            auto_size_columns=True)

    @property
    def columns(self) -> List[GridViewColumn]:
        return self._columns

    @columns.setter
    def columns(self, columns: List[GridViewColumn]) -> None:
        self._columns = columns
        self._options["columnDefs"] = [c.to_dict() for c in columns]
        self.update()
