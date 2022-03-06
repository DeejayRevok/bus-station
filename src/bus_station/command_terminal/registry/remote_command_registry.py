from abc import ABC, abstractmethod
from typing import Iterable, Optional, Tuple, Type

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.command_registry import CommandRegistry


class RemoteCommandRegistry(CommandRegistry, ABC):
    @abstractmethod
    def _register(self, command: Type[Command], handler: CommandHandler, handler_contact: str) -> None:
        pass

    @abstractmethod
    def get_command_destination_contact(self, command: Type[Command]) -> Optional[str]:
        pass

    @abstractmethod
    def get_commands_registered(self) -> Iterable[Tuple[Type[Command], CommandHandler, str]]:
        pass
