from redis import Redis

from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.registry.redis_registry import RedisRegistry


class RedisCommandRegistry(RedisRegistry, RemoteCommandRegistry):
    def __init__(self, client: Redis):
        RedisRegistry.__init__(self, client, InMemoryCommandRegistry())

    def register_destination(self, destination: CommandHandler, destination_contact: str) -> None:
        self._check_command_already_registered(destination)
        RedisRegistry.register_destination(self, destination, destination_contact)
