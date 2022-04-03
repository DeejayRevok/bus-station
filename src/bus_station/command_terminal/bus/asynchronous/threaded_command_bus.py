from threading import Thread
from typing import NoReturn

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver


class ThreadedCommandBus(CommandBus):
    def __init__(
        self, command_registry: InMemoryCommandRegistry, command_receiver: PassengerReceiver[Command, CommandHandler]
    ):
        super().__init__(command_receiver)
        self.__command_registry = command_registry

    def transport(self, passenger: Command) -> NoReturn:
        command_handler = self.__command_registry.get_command_destination_contact(passenger.__class__)
        if command_handler is None:
            raise HandlerNotFoundForCommand(passenger.__class__.__name__)

        execution_thread = Thread(target=self._command_receiver.receive, args=(passenger, command_handler))
        execution_thread.start()
