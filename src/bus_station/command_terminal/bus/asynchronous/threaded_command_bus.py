from threading import Thread

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_for_command_already_registered import HandlerForCommandAlreadyRegistered
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry


class ThreadedCommandBus(CommandBus):
    def __init__(self, command_registry: InMemoryRegistry):
        super().__init__()
        self.__command_registry = command_registry

    def register(self, handler: CommandHandler) -> None:
        handler_command = self._get_handler_command(handler)
        if handler_command in self.__command_registry:
            raise HandlerForCommandAlreadyRegistered(handler_command.__name__)
        self.__command_registry.register(handler_command, handler)

    def execute(self, command: Command) -> None:
        command_handler = self.__command_registry.get_passenger_destination(command.__class__)
        if command_handler is None:
            raise HandlerNotFoundForCommand(command.__class__.__name__)

        execution_thread = Thread(target=self._middleware_executor.execute, args=(command, command_handler))
        execution_thread.start()
