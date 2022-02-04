import os
import signal
from multiprocessing import Process
from typing import ClassVar, Optional

import requests
from jsonrpcclient import request

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_for_command_already_registered import HandlerForCommandAlreadyRegistered
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.jsonrpcserver_command_executor import JsonrpcserverCommandExecutor
from bus_station.passengers.registry.remote_registry import RemoteRegistry
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.runnable import Runnable, is_not_running, is_running


class JsonrpcserverCommandBus(CommandBus, Runnable):
    __SELF_ADDR_PATTERN: ClassVar[str] = "http://{host}:{port}/"

    def __init__(
        self,
        self_host: str,
        self_port: int,
        command_serializer: PassengerSerializer,
        command_deserializer: PassengerDeserializer,
        command_registry: RemoteRegistry,
    ):
        CommandBus.__init__(self)
        Runnable.__init__(self)
        self.__self_host = self_host
        self.__self_port = self_port
        self.__command_serializer = command_serializer
        self.__command_deserializer = command_deserializer
        self.__command_registry = command_registry
        self.__jsonrpcserver_command_executor = JsonrpcserverCommandExecutor(
            self.__command_deserializer,
            self._middleware_executor
        )
        self.__server_process: Optional[Process] = None

    def _start(self):
        self.__server_process = Process(target=self.__jsonrpcserver_command_executor.run, args=(self.__self_port,))
        self.__server_process.start()

    @is_not_running
    def register(self, handler: CommandHandler) -> None:
        handler_command = self._get_handler_command(handler)
        if handler_command in self.__command_registry:
            raise HandlerForCommandAlreadyRegistered(handler_command.__name__)

        self.__jsonrpcserver_command_executor.register(handler_command, handler)

        self_addr = self.__SELF_ADDR_PATTERN.format(host=self.__self_host, port=self.__self_port)
        self.__command_registry.register(handler_command, self_addr)

    @is_running
    def execute(self, command: Command) -> None:
        command_handler_addr = self.__command_registry.get_passenger_destination(command.__class__)
        if command_handler_addr is None:
            raise HandlerNotFoundForCommand(command.__class__.__name__)

        self.__execute_command(command, command_handler_addr)

    def __execute_command(self, command: Command, command_handler_addr: str) -> None:
        serialized_command = self.__command_serializer.serialize(command)
        requests.post(command_handler_addr, json=request(command.__class__.__name__, params=(serialized_command,)))

    def _stop(self) -> None:
        server_process = self.__server_process
        if server_process is not None and server_process.pid is not None:
            os.kill(server_process.pid, signal.SIGINT)
            server_process.join()
