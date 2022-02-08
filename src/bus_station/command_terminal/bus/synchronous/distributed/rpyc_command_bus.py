import os
import signal
from multiprocessing.context import Process
from typing import ClassVar, Optional

from rpyc import Connection, connect

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_for_command_already_registered import HandlerForCommandAlreadyRegistered
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.rpyc_command_service import RPyCCommandService
from bus_station.passengers.registry.remote_registry import RemoteRegistry
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.rpyc_server import RPyCServer
from bus_station.shared_terminal.runnable import Runnable, is_not_running


class RPyCCommandBus(CommandBus, Runnable):
    __SELF_ADDR_PATTERN: ClassVar[str] = "{host}:{port}"

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
        self.__rpyc_service = RPyCCommandService(self.__command_deserializer, self._middleware_executor)
        self.__rpyc_server: Optional[RPyCServer] = None
        self.__server_process: Optional[Process] = None

    def _start(self):
        self.__rpyc_server = RPyCServer(
            rpyc_service=self.__rpyc_service,
            port=self.__self_port,
        )
        self.__server_process = Process(target=self.__rpyc_server.run)
        self.__server_process.start()

    @is_not_running
    def register(self, handler: CommandHandler) -> None:
        handler_command = self._get_handler_command(handler)
        if handler_command in self.__command_registry:
            raise HandlerForCommandAlreadyRegistered(handler_command.__name__)

        self.__rpyc_service.register(handler_command, handler)

        self_addr = self.__SELF_ADDR_PATTERN.format(host=self.__self_host, port=self.__self_port)
        self.__command_registry.register(handler_command, self_addr)

    def execute(self, command: Command) -> None:
        command_handler_addr = self.__command_registry.get_passenger_destination(command.__class__)
        if command_handler_addr is None:
            raise HandlerNotFoundForCommand(command.__class__.__name__)

        rpyc_client = self.__get_rpyc_client(command_handler_addr)
        self.__execute_command(rpyc_client, command)
        rpyc_client.close()

    def __get_rpyc_client(self, handler_addr: str) -> Connection:
        host, port = handler_addr.split(":")
        return connect(host, port=port)

    def __execute_command(self, client: Connection, command: Command) -> None:
        serialized_command = self.__command_serializer.serialize(command)
        getattr(client.root, command.__class__.__name__)(serialized_command)

    def _stop(self) -> None:
        server_process = self.__server_process
        if server_process is not None and server_process.pid is not None:
            os.kill(server_process.pid, signal.SIGINT)
            server_process.join()
