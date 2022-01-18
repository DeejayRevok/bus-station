from abc import abstractmethod
from typing import get_type_hints, Type

from bus_station.command_terminal.middleware.command_middleware import CommandMiddleware
from bus_station.command_terminal.middleware.command_middleware_executor import CommandMiddlewareExecutor
from bus_station.shared_terminal.bus import Bus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler


class CommandBus(Bus[CommandHandler, CommandMiddleware]):
    def __init__(self):
        super().__init__(CommandMiddlewareExecutor)

    def _get_handler_command(self, handler: CommandHandler) -> Type[Command]:
        handle_typing = get_type_hints(handler.handle)

        if "command" not in handle_typing:
            raise TypeError(f"Handle command not found for {handler.__class__.__name__}")

        if not issubclass(handle_typing["command"], Command):
            raise TypeError(f"Wrong type for handle command of {handler.__class__.__name__}")

        return handle_typing["command"]

    @abstractmethod
    def execute(self, command: Command) -> None:
        pass
