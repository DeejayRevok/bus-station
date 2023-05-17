from rpyc import Connection, connect

from bus_station.bus_stop.registration.address.address_not_found_for_bus_stop import AddressNotFoundForBusStop
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.passengers.passenger_registry import passenger_bus_stop_registry
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
        command_handler_ids = passenger_bus_stop_registry.get_bus_stops_for_passenger(passenger.passenger_name())
        if len(command_handler_ids) == 0:
            raise HandlerNotFoundForCommand(passenger.passenger_name())

        command_handler_id = next(iter(command_handler_ids))
        handler_address = self.__address_registry.get_bus_stop_address(command_handler_id)
        if handler_address is None:
            raise AddressNotFoundForBusStop(command_handler_id)

        return handler_address

    def __get_rpyc_client(self, handler_addr: str) -> Connection:
        host, port = handler_addr.split(":")
        return connect(host, port=port, config={"allow_public_attrs": True})

    def __execute_command(self, client: Connection, command: Command) -> None:
        serialized_command = self.__command_serializer.serialize(command)
        getattr(client.root, command.passenger_name())(serialized_command)
