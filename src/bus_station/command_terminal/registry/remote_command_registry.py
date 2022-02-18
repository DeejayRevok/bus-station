from abc import ABC

from bus_station.command_terminal.registry.command_registry import CommandRegistry
from bus_station.passengers.registry.remote_registry import RemoteRegistry


class RemoteCommandRegistry(CommandRegistry, RemoteRegistry, ABC):
    pass
