from threading import Thread

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry


class ThreadedCommandBus(CommandBus):
    def __init__(self, command_registry: InMemoryCommandRegistry):
        super().__init__()
        self.__command_registry = command_registry

    def execute(self, command: Command) -> None:
        command_handler = self.__command_registry.get_command_destination_contact(command.__class__)
        if command_handler is None:
            raise HandlerNotFoundForCommand(command.__class__.__name__)

        execution_thread = Thread(target=self._middleware_executor.execute, args=(command, command_handler))
        execution_thread.start()
