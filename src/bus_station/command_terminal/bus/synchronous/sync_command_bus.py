from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver


class SyncCommandBus(CommandBus):
    def __init__(
        self,
        command_handler_registry: CommandHandlerRegistry,
        command_receiver: PassengerReceiver[Command, CommandHandler],
    ):
        self.__command_handler_registry = command_handler_registry
        self.__command_receiver = command_receiver

    def _transport(self, passenger: Command) -> None:
        command_handler = self.__command_handler_registry.get_handler_from_command(passenger.passenger_name())
        if command_handler is None:
            raise HandlerNotFoundForCommand(passenger.passenger_name())
        self.__command_receiver.receive(passenger, command_handler)
