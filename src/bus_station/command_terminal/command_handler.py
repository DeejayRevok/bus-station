from abc import abstractmethod

from bus_station.command_terminal.command import Command
from bus_station.shared_terminal.bus_stop import BusStop


class CommandHandler(BusStop):
    @abstractmethod
    def handle(self, command: Command) -> None:
        pass

    @classmethod
    def bus_stop_name(cls) -> str:
        return f"command_handler.{cls.__module__}.{cls.__name__}"
