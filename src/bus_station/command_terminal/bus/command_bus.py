from abc import abstractmethod

from bus_station.command_terminal.command import Command
from bus_station.shared_terminal.bus import Bus


class CommandBus(Bus[Command]):
    @abstractmethod
    def transport(self, passenger: Command) -> None:
        pass
