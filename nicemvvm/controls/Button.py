from typing import Mapping, Any

from nicegui import ui

from nicemvvm.Command import Command
from nicemvvm.observables.Observable import Observer


class Button(ui.button, Observer):
    def __init__(self, text:str,
                 color: str = "primary",
                 icon: str|None = None,
                 command: Command|None = None
                 ):
        ui.button.__init__(self, text=text, color=color, icon=icon)

        self._command: Command|None = command
        if command is not None:
            self.on("click", command.run)
            command.register(self._command_handler)

    def _command_handler(self,
                         action: str,
                         args: Mapping[str, Any]) -> None:
        if action == "property":
            if args["name"] == "is_enabled":
                enabled = args["value"]
                if enabled:
                    self.enable()
                else:
                    self.disable()

    @property
    def command(self) -> Command|None:
        return self._command

    @command.setter
    def command(self, command: Command) -> None:
        if self._command != command:
            self._command = command
            self.on("click", command.run)

            command.register(self._command_handler)