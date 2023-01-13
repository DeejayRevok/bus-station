from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver


class SyncCommandBus(CommandBus):
    def __init__(
        self, command_registry: InMemoryCommandRegistry, command_receiver: PassengerReceiver[Command, CommandHandler]
    ):
        self.__command_registry = command_registry
        self.__command_receiver = command_receiver

    def transport(self, passenger: Command) -> None:
        command_handler = self.__command_registry.get_command_destination_contact(passenger.passenger_name())
        if command_handler is None:
            raise HandlerNotFoundForCommand(passenger.passenger_name())
        self.__command_receiver.receive(passenger, command_handler)
