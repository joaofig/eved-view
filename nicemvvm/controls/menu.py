from typing import Optional, Mapping, Any

from nicegui import ui
from nicegui.events import Handler, ClickEventArguments

from nicemvvm.command import Command
from nicemvvm.observables.observability import Observer


class MenuItem(ui.menu_item, Observer):
    def __init__(self, text: str = "",
                 command: Command | None = None,
                 on_click: Optional[Handler[ClickEventArguments]] = None,
                 *,
                 auto_close: bool = True) -> None:
        super().__init__(text, on_click, auto_close=auto_close)

        self._command: Command | None = command
        if command is not None:
            self.on("click", command.execute)
            command.register(self._command_handler)

    def _command_handler(self, action: str, args: Mapping[str, Any]) -> None:
        if action == "property_changed":
            if args["name"] == "is_enabled":
                enabled = args["value"]
                if enabled:
                    self.enable()
                else:
                    self.disable()

    @property
    def command(self) -> Command | None:
        return self._command

    @command.setter
    def command(self, command: Command) -> None:
        if self._command != command:
            self._command = command
            self.on("click", command.execute)

            command.register(self._command_handler)
