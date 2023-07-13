from abc import abstractmethod
from typing import Type

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.command_terminal.command import Command
from bus_station.shared_terminal.dataclass_type import DataclassType


class CommandHandler(BusStop):
    @abstractmethod
    def handle(self, command: Command | DataclassType) -> None:
        pass

    @classmethod
    def bus_stop_name(cls) -> str:
        return f"command_handler.{cls.__module__}.{cls.__name__}"

    @classmethod
    def passenger(cls) -> Type[Command]:
        passenger = cls._get_passenger_from_handling_method(cls.handle, "command")
        return passenger
