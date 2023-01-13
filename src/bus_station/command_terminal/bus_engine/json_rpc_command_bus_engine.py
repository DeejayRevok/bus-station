from bus_station.command_terminal.command import Command
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.json_rpc_command_server import JsonRPCCommandServer
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.resolve_passenger_from_bus_stop import resolve_passenger_from_bus_stop
from bus_station.shared_terminal.engine.engine import Engine


class JsonRPCCommandBusEngine(Engine):
    def __init__(
        self,
        server: JsonRPCCommandServer,
        command_registry: RemoteCommandRegistry,
        command_name: str,
    ):
        super().__init__()
        self.__server = server
        self.__register_command_in_server(command_registry, command_name)

    def __register_command_in_server(self, command_registry: RemoteCommandRegistry, command_name: str) -> None:
        handler = command_registry.get_command_destination(command_name)
        if handler is None:
            raise HandlerNotFoundForCommand(command_name)
        command_type = resolve_passenger_from_bus_stop(handler, "handle", "command", Command)
        self.__server.register(command_type, handler)

    def start(self) -> None:
        self.__server.run()

    def stop(self):
        pass
