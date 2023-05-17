import requests
from jsonrpcclient import Error, parse, request

from bus_station.bus_stop.registration.address.address_not_found_for_bus_stop import AddressNotFoundForBusStop
from bus_station.bus_stop.registration.address.bus_stop_address_registry import BusStopAddressRegistry
from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_execution_failed import CommandExecutionFailed
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.passengers.passenger_registry import passenger_bus_stop_registry
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
        command_handler_ids = passenger_bus_stop_registry.get_bus_stops_for_passenger(passenger.passenger_name())
        if len(command_handler_ids) == 0:
            raise HandlerNotFoundForCommand(passenger.passenger_name())

        command_handler_id = next(iter(command_handler_ids))
        handler_address = self.__address_registry.get_bus_stop_address(command_handler_id)
        if handler_address is None:
            raise AddressNotFoundForBusStop(command_handler_id)

        return handler_address

    def __execute_command(self, command: Command, command_handler_addr: str) -> None:
        serialized_command = self.__command_serializer.serialize(command)

        request_response = requests.post(
            command_handler_addr, json=request(command.__class__.passenger_name(), params=(serialized_command,))
        )
        json_rpc_response = parse(request_response.json())

        if isinstance(json_rpc_response, Error):
            raise CommandExecutionFailed(command, json_rpc_response.message)
