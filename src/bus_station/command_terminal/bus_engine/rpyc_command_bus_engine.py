from bus_station.command_terminal.command import Command
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.command_registry import CommandRegistry
from bus_station.passengers.resolve_passenger_from_bus_stop import resolve_passenger_from_bus_stop
from bus_station.shared_terminal.engine.engine import Engine
from bus_station.shared_terminal.rpyc_server import RPyCServer


class RPyCCommandBusEngine(Engine):
    def __init__(self, rpyc_server: RPyCServer, command_registry: CommandRegistry, command_name: str):
        super().__init__()
        self.__server = rpyc_server
        self.__register_command_in_server(command_registry, command_name)

    def __register_command_in_server(self, command_registry: CommandRegistry, command_name: str) -> None:
        handler = command_registry.get_command_destination(command_name)
        if handler is None:
            raise HandlerNotFoundForCommand(command_name)
        command_type = resolve_passenger_from_bus_stop(handler, "handle", "command", Command)
        self.__server.register(command_type, handler)

    def start(self) -> None:
        self.__server.run()

    def stop(self) -> None:
        pass
