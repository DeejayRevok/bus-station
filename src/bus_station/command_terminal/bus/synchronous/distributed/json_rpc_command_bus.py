import os
import signal
from multiprocessing import Process
from typing import ClassVar, Optional

import requests
from jsonrpcclient import request
from jsonrpcclient.responses import Error, to_result

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_execution_failed import CommandExecutionFailed
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.json_rpc_command_server import JsonRPCCommandServer
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.runnable import Runnable


class JsonRPCCommandBus(CommandBus, Runnable):
    __SELF_ADDR_PATTERN: ClassVar[str] = "http://{host}:{port}/"

    def __init__(
        self,
        self_host: str,
        self_port: int,
        command_serializer: PassengerSerializer,
        command_deserializer: PassengerDeserializer,
        command_registry: RemoteCommandRegistry,
        command_receiver: PassengerReceiver[Command, CommandHandler],
    ):
        CommandBus.__init__(self, command_receiver)
        Runnable.__init__(self)
        self.__self_host = self_host
        self.__self_port = self_port
        self.__command_serializer = command_serializer
        self.__command_deserializer = command_deserializer
        self.__command_registry = command_registry
        self.__json_rpc_command_server = JsonRPCCommandServer(
            passenger_deserializer=self.__command_deserializer, passenger_receiver=self._command_receiver
        )
        self.__server_process: Optional[Process] = None

    def _start(self):
        for command in self.__command_registry.get_commands_registered():
            handler = self.__command_registry.get_command_destination(command)
            self.__json_rpc_command_server.register(command, handler)

        self.__server_process = Process(target=self.__json_rpc_command_server.run, args=(self.__self_port,))
        self.__server_process.start()

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

    def _stop(self) -> None:
        server_process = self.__server_process
        if server_process is not None and server_process.pid is not None:
            os.kill(server_process.pid, signal.SIGINT)
            server_process.join()
