import requests
from jsonrpcclient import Error, parse, request

from bus_station.bus_stop.registration.address.address_not_found_for_passenger import AddressNotFoundForPassenger
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_execution_failed import CommandExecutionFailed
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class JsonRPCCommandBus(CommandBus):
    def __init__(
        self,
        command_serializer: PassengerSerializer,
        address_registry: BusStopAddressRegistry,
    ):
        self.__command_serializer = command_serializer
        self.__address_registry = address_registry

    def _transport(self, passenger: Command) -> None:
        handler_address = self.__get_handler_address(passenger)

        self.__execute_command(passenger, handler_address)

    def __get_handler_address(self, passenger: Command) -> str:
        handler_address = self.__address_registry.get_address_for_bus_stop_passenger_class(passenger.__class__)
        if handler_address is None:
            raise AddressNotFoundForPassenger(passenger.passenger_name())

        return handler_address

    def __execute_command(self, command: Command, command_handler_addr: str) -> None:
        serialized_command = self.__command_serializer.serialize(command)

        request_response = requests.post(
            command_handler_addr, json=request(command.__class__.passenger_name(), params=(serialized_command,))
        )
        json_rpc_response = parse(request_response.json())

        if isinstance(json_rpc_response, Error):
            raise CommandExecutionFailed(command, json_rpc_response.message)
