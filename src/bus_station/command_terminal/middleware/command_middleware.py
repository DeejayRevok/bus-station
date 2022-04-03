from abc import abstractmethod

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.passengers.passenger_middleware import PassengerMiddleware


class CommandMiddleware(PassengerMiddleware):
    @abstractmethod
    def before_handle(self, passenger: Command, bus_stop: CommandHandler) -> None:
        pass

    @abstractmethod
    def after_handle(self, passenger: Command, bus_stop: CommandHandler) -> None:
        pass
