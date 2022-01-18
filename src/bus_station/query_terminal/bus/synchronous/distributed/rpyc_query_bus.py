import os
import signal
from multiprocessing import Process
from typing import ClassVar, Optional

from rpyc import ThreadedServer, Connection, connect

from bus_station.passengers.registry.remote_registry import RemoteRegistry
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.rpyc_query_service import RPyCQueryService
from bus_station.query_terminal.bus.query_bus import QueryBus
from bus_station.query_terminal.handler_for_query_already_registered import HandlerForQueryAlreadyRegistered
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.serialization.query_response_deserializer import QueryResponseDeserializer
from bus_station.query_terminal.serialization.query_response_serializer import QueryResponseSerializer
from bus_station.shared_terminal.runnable import Runnable, is_not_running, is_running


class RPyCQueryBus(QueryBus, Runnable):
    __SELF_ADDR_PATTERN: ClassVar[str] = "{host}:{port}"

    def __init__(
        self,
        self_host: str,
        self_port: int,
        query_serializer: PassengerSerializer,
        query_deserializer: PassengerDeserializer,
        query_response_serializer: QueryResponseSerializer,
        query_response_deserializer: QueryResponseDeserializer,
        query_registry: RemoteRegistry,
    ):
        QueryBus.__init__(self)
        Runnable.__init__(self)
        self.__self_host = self_host
        self.__self_port = self_port
        self.__query_serializer = query_serializer
        self.__query_deserializer = query_deserializer
        self.__query_response_serializer = query_response_serializer
        self.__query_response_deserializer = query_response_deserializer
        self.__query_registry = query_registry
        self.__rpyc_service = RPyCQueryService(
            self.__query_deserializer, self.__query_response_serializer, self._middleware_executor
        )
        self.__rpyc_server: Optional[ThreadedServer] = None
        self.__server_process: Optional[Process] = None

    def _start(self):
        self.__rpyc_server = ThreadedServer(
            self.__rpyc_service,
            hostname=self.__self_host,
            port=self.__self_port,
        )
        self.__server_process = Process(target=self.__rpyc_server.start)
        self.__server_process.start()

    @is_not_running
    def register(self, handler: QueryHandler) -> None:
        handler_query = self._get_handler_query(handler)
        if handler_query in self.__query_registry:
            raise HandlerForQueryAlreadyRegistered(handler_query.__name__)

        self.__rpyc_service.register(handler_query, handler)

        self_addr = self.__SELF_ADDR_PATTERN.format(host=self.__self_host, port=self.__self_port)
        self.__query_registry.register(handler_query, self_addr)

    @is_running
    def execute(self, query: Query) -> QueryResponse:
        query_handler_addr = self.__query_registry.get_passenger_destination(query.__class__)
        if query_handler_addr is None:
            raise HandlerNotFoundForQuery(query.__class__.__name__)

        rpyc_client = self.__get_rpyc_client(query_handler_addr)
        query_response = self.__execute_query(rpyc_client, query)
        rpyc_client.close()
        return query_response

    def __get_rpyc_client(self, handler_addr: str) -> Connection:
        host, port = handler_addr.split(":")
        return connect(host, port=port)

    def __execute_query(self, client: Connection, query: Query) -> QueryResponse:
        serialized_query = self.__query_serializer.serialize(query)
        serialized_query_response = getattr(client.root, query.__class__.__name__)(serialized_query)
        return self.__query_response_deserializer.deserialize(serialized_query_response)

    def _stop(self) -> None:
        server_process = self.__server_process
        if server_process is not None and server_process.pid is not None:
            os.kill(server_process.pid, signal.SIGINT)
            server_process.join()
