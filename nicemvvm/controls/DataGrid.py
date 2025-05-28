from typing import Any
from nicegui.elements.aggrid import (AgGrid)

from nicemvvm.Observable import Observable


class DataGrid(AgGrid):
    def __init__(self):
        self._options = {
            "columnDefs": [],
            "rowData": [],
        }
        super().__init__(
            options=self._options,
            auto_size_columns=True)

        self.items_source: str = ""
        self.selected_item: str = ""
        self._data_source: Observable|None = None

    @property
    def data_source(self):
        return self._data_source

    @data_source.setter
    def data_source(self, value: Observable|None):
        if value is None:
            if self._data_source is not None:
                self._data_source.unbind(self._observer)
        else:
            value.bind(self._observer)
        self._data_source = value

    def _observer(self, _: Any, property_name: str, value: Any) -> None:
        if property_name == self.items_source :
            self._options["rowData"] = value
            self.update()
        elif property_name == self.selected_item:
            ...
