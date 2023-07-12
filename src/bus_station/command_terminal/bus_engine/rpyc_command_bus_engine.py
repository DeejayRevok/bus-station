from bus_station.command_terminal.command_handler_not_found import CommandHandlerNotFound
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.shared_terminal.engine.engine import Engine
from bus_station.shared_terminal.rpyc_server import RPyCServer


class RPyCCommandBusEngine(Engine):
    def __init__(
        self, rpyc_server: RPyCServer, command_handler_registry: CommandHandlerRegistry, command_handler_name: str
    ):
        self.__server = rpyc_server
        self.__register_command_in_server(command_handler_registry, command_handler_name)

    def __register_command_in_server(
        self, command_handler_registry: CommandHandlerRegistry, command_handler_name: str
    ) -> None:
        handler = command_handler_registry.get_bus_stop_by_name(command_handler_name)
        if handler is None:
            raise CommandHandlerNotFound(command_handler_name)
        command_type = handler.passenger()
        self.__server.register(command_type, handler)

    def start(self) -> None:
        self.__server.run()

    def stop(self) -> None:
        pass
