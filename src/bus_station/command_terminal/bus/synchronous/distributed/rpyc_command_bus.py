from rpyc import Connection, connect

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class RPyCCommandBus(CommandBus):
    def __init__(
        self,
        command_serializer: PassengerSerializer,
        command_registry: RemoteCommandRegistry,
    ):
        self.__command_serializer = command_serializer
        self.__command_registry = command_registry

    def transport(self, passenger: Command) -> None:
        handler_address = self.__command_registry.get_command_destination_contact(passenger.__class__)
        if handler_address is None:
            raise HandlerNotFoundForCommand(passenger.__class__.__name__)

        rpyc_client = self.__get_rpyc_client(handler_address)
        self.__execute_command(rpyc_client, passenger)
        rpyc_client.close()

    def __get_rpyc_client(self, handler_addr: str) -> Connection:
        host, port = handler_addr.split(":")
        return connect(host, port=port, config={"allow_public_attrs": True})

    def __execute_command(self, client: Connection, command: Command) -> None:
        serialized_command = self.__command_serializer.serialize(command)
        getattr(client.root, command.__class__.__name__)(serialized_command)
