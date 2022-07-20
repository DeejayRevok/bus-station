from abc import abstractmethod

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.shared_terminal.bus import Bus


class CommandBus(Bus[Command]):
    def __init__(self, command_receiver: PassengerReceiver[Command, CommandHandler]):
        self._command_receiver = command_receiver

    @abstractmethod
    def transport(self, passenger: Command) -> None:
        pass
