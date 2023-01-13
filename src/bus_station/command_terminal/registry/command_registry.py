from abc import ABCMeta, abstractmethod
from typing import Any, Iterable, Optional, Type

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_for_command_already_registered import HandlerForCommandAlreadyRegistered
from bus_station.passengers.resolve_passenger_from_bus_stop import resolve_passenger_from_bus_stop


class CommandRegistry(metaclass=ABCMeta):
    def register(self, handler: CommandHandler, handler_contact: Any) -> None:
        handler_command = resolve_passenger_from_bus_stop(handler, "handle", "command", Command)
        existing_handler_contact = self.get_command_destination_contact(handler_command.passenger_name())
        self.__check_command_already_registered(handler_command, handler_contact, existing_handler_contact)
        if existing_handler_contact is None:
            self._register(handler_command, handler, handler_contact)

    def __check_command_already_registered(
        self, command: Type[Command], handler_contact: Any, existing_handler_contact: Optional[Any]
    ) -> None:
        if existing_handler_contact is not None and handler_contact != existing_handler_contact:
            raise HandlerForCommandAlreadyRegistered(command.passenger_name())

    @abstractmethod
    def _register(self, command: Type[Command], handler: CommandHandler, handler_contact: Any) -> None:
        pass

    @abstractmethod
    def get_command_destination(self, command_name: str) -> Optional[CommandHandler]:
        pass

    @abstractmethod
    def get_command_destination_contact(self, command_name: str) -> Optional[Any]:
        pass

    @abstractmethod
    def get_commands_registered(self) -> Iterable[Type[Command]]:
        pass

    @abstractmethod
    def unregister(self, command_name: str) -> None:
        pass
