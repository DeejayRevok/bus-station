from abc import ABCMeta, abstractmethod
from typing import Any, Iterable, Optional, Type, get_type_hints

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_for_command_already_registered import HandlerForCommandAlreadyRegistered


class CommandRegistry(metaclass=ABCMeta):
    def register(self, handler: CommandHandler, handler_contact: Any) -> None:
        handler_command = self.__get_handler_command(handler)
        self.__check_command_already_registered(handler_command)
        self._register(handler_command, handler, handler_contact)

    def __check_command_already_registered(self, command: Type[Command]) -> None:
        if self.get_command_destination_contact(command) is not None:
            raise HandlerForCommandAlreadyRegistered(command.__name__)

    def __get_handler_command(self, handler: CommandHandler) -> Type[Command]:
        handle_typing = get_type_hints(handler.handle)

        if "command" not in handle_typing:
            raise TypeError(f"Handle command not found for {handler.__class__.__name__}")

        if not issubclass(handle_typing["command"], Command):
            raise TypeError(f"Wrong type for handle command of {handler.__class__.__name__}")

        return handle_typing["command"]

    @abstractmethod
    def _register(self, command: Type[Command], handler: CommandHandler, handler_contact: Any) -> None:
        pass

    @abstractmethod
    def get_command_destination(self, command: Type[Command]) -> Optional[CommandHandler]:
        pass

    @abstractmethod
    def get_command_destination_contact(self, command: Type[Command]) -> Optional[Any]:
        pass

    @abstractmethod
    def get_commands_registered(self) -> Iterable[Type[Command]]:
        pass

    @abstractmethod
    def unregister(self, command: Type[Command]) -> None:
        pass
