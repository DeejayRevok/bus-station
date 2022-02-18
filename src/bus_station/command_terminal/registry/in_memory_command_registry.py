from typing import Any

from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.command_registry import CommandRegistry
from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry


class InMemoryCommandRegistry(InMemoryRegistry, CommandRegistry):
    def register_destination(self, destination: CommandHandler, destination_contact: Any) -> None:
        self._check_command_already_registered(destination)
        InMemoryRegistry.register_destination(self, destination, destination_contact)
