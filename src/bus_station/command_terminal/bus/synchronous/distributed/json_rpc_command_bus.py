import requests
from jsonrpcclient import request
from jsonrpcclient.responses import Error, to_result

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_execution_failed import CommandExecutionFailed
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class JsonRPCCommandBus(CommandBus):
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

        self.__execute_command(passenger, handler_address)

    def __execute_command(self, command: Command, command_handler_addr: str) -> None:
        serialized_command = self.__command_serializer.serialize(command)

        request_response = requests.post(
            command_handler_addr, json=request(command.__class__.__name__, params=(serialized_command,))
        )
        json_rpc_response = to_result(request_response.json())

        if isinstance(json_rpc_response, Error):
            raise CommandExecutionFailed(command, json_rpc_response.message)
