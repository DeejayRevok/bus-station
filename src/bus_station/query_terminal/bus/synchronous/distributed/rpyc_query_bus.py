import os
import signal
from multiprocessing import Process
from typing import ClassVar, Optional

from rpyc import Connection, connect

from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.bus.query_bus import QueryBus
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.registry.remote_query_registry import RemoteQueryRegistry
from bus_station.query_terminal.rpyc_query_service import RPyCQueryService
from bus_station.query_terminal.serialization.query_response_deserializer import QueryResponseDeserializer
from bus_station.query_terminal.serialization.query_response_serializer import QueryResponseSerializer
from bus_station.shared_terminal.rpyc_server import RPyCServer
from bus_station.shared_terminal.runnable import Runnable


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
        query_registry: RemoteQueryRegistry,
        query_receiver: PassengerReceiver[Query, QueryHandler],
    ):
        QueryBus.__init__(self, query_receiver)
        Runnable.__init__(self)
        self.__self_host = self_host
        self.__self_port = self_port
        self.__query_serializer = query_serializer
        self.__query_deserializer = query_deserializer
        self.__query_response_serializer = query_response_serializer
        self.__query_response_deserializer = query_response_deserializer
        self.__query_registry = query_registry
        self.__rpyc_service = RPyCQueryService(
            self.__query_deserializer, self.__query_response_serializer, self._query_receiver
        )
        self.__rpyc_server: Optional[RPyCServer] = None
        self.__server_process: Optional[Process] = None

    def _start(self):
        for query in self.__query_registry.get_queries_registered():
            handler = self.__query_registry.get_query_destination(query)
            self.__rpyc_service.register(query, handler)

        self.__rpyc_server = RPyCServer(
            rpyc_service=self.__rpyc_service,
            port=self.__self_port,
        )
        self.__server_process = Process(target=self.__rpyc_server.run)
        self.__server_process.start()

    def transport(self, passenger: Query) -> QueryResponse:
        query_handler_addr = self.__query_registry.get_query_destination_contact(passenger.__class__)
        if query_handler_addr is None:
            raise HandlerNotFoundForQuery(passenger.__class__.__name__)

        rpyc_client = self.__get_rpyc_client(query_handler_addr)
        query_response = self.__execute_query(rpyc_client, passenger)
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
