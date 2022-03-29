from abc import abstractmethod

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.middleware.command_middleware import CommandMiddleware
from bus_station.command_terminal.middleware.command_middleware_executor import CommandMiddlewareExecutor
from bus_station.shared_terminal.bus import Bus


class CommandBus(Bus[CommandMiddleware]):
    def __init__(self):
        super().__init__(CommandMiddlewareExecutor)

    @abstractmethod
    def execute(self, command: Command) -> None:
        pass
