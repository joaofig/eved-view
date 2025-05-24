from typing import List

from nicegui import ui
from src.message import ObservableList
from src.ui.viewmodels.BaseViewModel import BaseViewModel


class GridView:
    def __init__(self,
                 column_defs: List|None = None):
        self._prop_name: str|None = None
        self._column_defs = [] if column_defs is None else column_defs
        self._source: ObservableList|None = None
        self._options = {
            "columnDefs": self._column_defs,
            "rowData": [],
            "loading": False,
        }

        self._grid = ui.aggrid(options=self._options)


    def _refresh_rows(self):
        self._options["rowData"] = self._source
        self._grid.update()

    def _list_observer(self, *args, **kwargs):
        if "action" in kwargs:
            self._refresh_rows()

    def bind(self, observable_list: ObservableList) -> None:
        self._source = observable_list
        self._source.subscribe(self._list_observer)
        self._refresh_rows()

    def add_column(self,
                   field_name: str,
                   header_name: str = "",
                   column_filter: bool = False,
                   column_type: str = "",
                   editable: bool = False,
                   cell_editor: str = "",
                   checkbox_selection: bool = False,
                   header_checkbox_selection: bool = False,
                   ) -> None:
        column = {
            "field": field_name,
            "headerName": header_name,
            "filter": column_filter,
            "editable": editable,
            "checkboxSelection": checkbox_selection,
            "headerCheckboxSelection": header_checkbox_selection,
        }
        if cell_editor:
            column["cellEditor"] = cell_editor
        if type:
            column["type"] = column_type

        self._column_defs.append(column)
        self._grid.update()
