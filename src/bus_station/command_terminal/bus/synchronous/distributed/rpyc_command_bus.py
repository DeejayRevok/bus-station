from rpyc import Connection, connect

from bus_station.bus_stop.registration.address.address_not_found_for_passenger import AddressNotFoundForPassenger
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class RPyCCommandBus(CommandBus):
    def __init__(
        self,
        command_serializer: PassengerSerializer,
        address_registry: BusStopAddressRegistry,
    ):
        self.__command_serializer = command_serializer
        self.__address_registry = address_registry

    def _transport(self, passenger: Command) -> None:
        handler_address = self.__get_handler_address(passenger)

        rpyc_client = self.__get_rpyc_client(handler_address)
        self.__execute_command(rpyc_client, passenger)

        rpyc_client.close()

    def __get_handler_address(self, passenger: Command) -> str:
        handler_address = self.__address_registry.get_address_for_bus_stop_passenger_class(passenger.__class__)
        if handler_address is None:
            raise AddressNotFoundForPassenger(passenger.passenger_name())

        return handler_address

    def __get_rpyc_client(self, handler_addr: str) -> Connection:
        host, port = handler_addr.split(":")
        return connect(host, port=port, config={"allow_public_attrs": True})

    def __execute_command(self, client: Connection, command: Command) -> None:
        serialized_command = self.__command_serializer.serialize(command)
        getattr(client.root, command.passenger_name())(serialized_command)
