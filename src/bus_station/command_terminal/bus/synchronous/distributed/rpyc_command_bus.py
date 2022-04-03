import os
import signal
from multiprocessing.context import Process
from typing import ClassVar, NoReturn, Optional

from rpyc import Connection, connect

from bus_station.command_terminal.bus.command_bus import CommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.command_terminal.rpyc_command_service import RPyCCommandService
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.rpyc_server import RPyCServer
from bus_station.shared_terminal.runnable import Runnable


class RPyCCommandBus(CommandBus, Runnable):
    __SELF_ADDR_PATTERN: ClassVar[str] = "{host}:{port}"

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
        self.__rpyc_service = RPyCCommandService(self.__command_deserializer, self._command_receiver)
        self.__rpyc_server: Optional[RPyCServer] = None
        self.__server_process: Optional[Process] = None

    def _start(self):
        for command in self.__command_registry.get_commands_registered():
            handler = self.__command_registry.get_command_destination(command)
            self.__rpyc_service.register(command, handler)

        self.__rpyc_server = RPyCServer(
            rpyc_service=self.__rpyc_service,
            port=self.__self_port,
        )
        self.__server_process = Process(target=self.__rpyc_server.run)
        self.__server_process.start()

    def transport(self, passenger: Command) -> NoReturn:
        handler_address = self.__command_registry.get_command_destination_contact(passenger.__class__)
        if handler_address is None:
            raise HandlerNotFoundForCommand(passenger.__class__.__name__)

        rpyc_client = self.__get_rpyc_client(handler_address)
        self.__execute_command(rpyc_client, passenger)
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
