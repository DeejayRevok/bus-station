from abc import ABC
from typing import Type, Any, get_type_hints

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_for_command_already_registered import HandlerForCommandAlreadyRegistered
from bus_station.passengers.passenger import Passenger
from bus_station.passengers.registry.passenger_registry import PassengerRegistry


class CommandRegistry(PassengerRegistry[CommandHandler, Any], ABC):

    def _get_destination_passenger(self, destination: CommandHandler) -> Type[Passenger]:
        handle_typing = get_type_hints(destination.handle)

        if "command" not in handle_typing:
            raise TypeError(f"Handle command not found for {destination.__class__.__name__}")

        if not issubclass(handle_typing["command"], Command):
            raise TypeError(f"Wrong type for handle command of {destination.__class__.__name__}")

        return handle_typing["command"]

    def _check_command_already_registered(self, destination: CommandHandler) -> None:
        handler_command = self._get_destination_passenger(destination)
        if handler_command in self:
            raise HandlerForCommandAlreadyRegistered(handler_command.__name__)
