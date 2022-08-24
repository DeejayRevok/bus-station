from typing import Optional, Type, TypeVar

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.registry.command_registry import CommandRegistry
from bus_station.shared_terminal.engine.engine import Engine
from bus_station.shared_terminal.rpyc_server import RPyCServer

C = TypeVar("C", bound=Command)


class RPyCCommandBusEngine(Engine):
    def __init__(
        self, rpyc_server: RPyCServer, command_registry: CommandRegistry, command_type: Optional[Type[C]] = None
    ):
        super().__init__()
        self.__server = rpyc_server

        if command_type is not None:
            self.__register_command_in_server(command_registry, command_type)
            return

        for command_type in command_registry.get_commands_registered():
            self.__register_command_in_server(command_registry, command_type)

    def __register_command_in_server(self, command_registry: CommandRegistry, command_type: Type[C]) -> None:
        handler = command_registry.get_command_destination(command_type)
        self.__server.register(command_type, handler)

    def start(self) -> None:
        self.__server.run()

    def stop(self) -> None:
        pass
