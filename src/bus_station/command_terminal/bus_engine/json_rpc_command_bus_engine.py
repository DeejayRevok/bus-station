from typing import Optional, Type, TypeVar

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.json_rpc_command_server import JsonRPCCommandServer
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.shared_terminal.engine.engine import Engine

C = TypeVar("C", bound=Command)


class JsonRPCCommandBusEngine(Engine):
    def __init__(
        self,
        server: JsonRPCCommandServer,
        command_registry: RemoteCommandRegistry,
        command_type: Optional[Type[C]] = None,
    ):
        super().__init__()
        self.__server = server
        if command_type is not None:
            self.__register_command_in_server(command_registry, command_type)
            return

        for command_type in command_registry.get_commands_registered():
            self.__register_command_in_server(command_registry, command_type)

    def __register_command_in_server(self, command_registry: RemoteCommandRegistry, command_type: Type[C]) -> None:
        handler = command_registry.get_command_destination(command_type)
        if handler is None:
            raise HandlerNotFoundForCommand(command_type.__name__)
        self.__server.register(command_type, handler)

    def start(self) -> None:
        self.__server.run()

    def stop(self):
        pass
