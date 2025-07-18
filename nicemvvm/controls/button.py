from typing import Any, Mapping

from nicegui import ui

from nicemvvm.command import Command
from nicemvvm.observables.observability import Observer


class Button(ui.button, Observer):
    def __init__(
        self,
        text: str,
        color: str = "primary",
        icon: str | None = None,
        command: Command | None = None,
    ):
        ui.button.__init__(self, text=text, color=color, icon=icon)

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
