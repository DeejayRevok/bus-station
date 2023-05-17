from bus_station.command_terminal.command_handler_not_found import CommandHandlerNotFound
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.command_terminal.json_rpc_command_server import JsonRPCCommandServer
from bus_station.passengers.passenger_resolvers import resolve_passenger_class_from_bus_stop
from bus_station.shared_terminal.engine.engine import Engine


class JsonRPCCommandBusEngine(Engine):
    def __init__(
        self,
        server: JsonRPCCommandServer,
        command_handler_registry: CommandHandlerRegistry,
        command_handler_name: str,
    ):
        self.__server = server
        self.__register_command_handler_in_server(command_handler_registry, command_handler_name)

    def __register_command_handler_in_server(
        self, command_handler_registry: CommandHandlerRegistry, command_handler_name: str
    ) -> None:
        handler = command_handler_registry.get_bus_stop_by_name(command_handler_name)
        if handler is None:
            raise CommandHandlerNotFound(command_handler_name)

        command_type = resolve_passenger_class_from_bus_stop(handler, "handle", "command")
        self.__server.register(command_type, handler)

    def start(self) -> None:
        self.__server.run()

    def stop(self):
        pass
