from abc import abstractmethod

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.command_terminal.command import Command


class CommandHandler(BusStop):
    @abstractmethod
    def handle(self, command: Command) -> None:
        pass

    @classmethod
    def bus_stop_name(cls) -> str:
        return f"command_handler.{cls.__module__}.{cls.__name__}"
