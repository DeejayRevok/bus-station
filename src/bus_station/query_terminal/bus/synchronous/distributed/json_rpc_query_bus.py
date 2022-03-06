import os
import signal
from multiprocessing import Process
from typing import ClassVar, Optional

import requests
from jsonrpcclient import request
from jsonrpcclient.responses import Error, to_result

from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.bus.query_bus import QueryBus
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.json_rpc_query_server import JsonRPCQueryServer
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_execution_failed import QueryExecutionFailed
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.registry.remote_query_registry import RemoteQueryRegistry
from bus_station.query_terminal.serialization.query_response_deserializer import QueryResponseDeserializer
from bus_station.query_terminal.serialization.query_response_serializer import QueryResponseSerializer
from bus_station.shared_terminal.runnable import Runnable


class JsonRPCQueryBus(QueryBus, Runnable):
    __SELF_ADDR_PATTERN: ClassVar[str] = "http://{host}:{port}/"

    def __init__(
        self,
        self_host: str,
        self_port: int,
        query_serializer: PassengerSerializer,
        query_deserializer: PassengerDeserializer,
        query_response_serializer: QueryResponseSerializer,
        query_response_deserializer: QueryResponseDeserializer,
        query_registry: RemoteQueryRegistry,
    ):
        QueryBus.__init__(self)
        Runnable.__init__(self)
        self.__self_host = self_host
        self.__self_port = self_port
        self.__query_serializer = query_serializer
        self.__query_deserializer = query_deserializer
        self.__query_registry = query_registry
        self.__query_response_serializer = query_response_serializer
        self.__query_response_deserializer = query_response_deserializer
        self.__json_rpc_query_server = JsonRPCQueryServer(
            passenger_deserializer=self.__query_deserializer,
            passenger_middleware_executor=self._middleware_executor,
            query_response_serializer=self.__query_response_serializer,
        )
        self.__server_process: Optional[Process] = None

    def _start(self):
        for query, handler, _ in self.__query_registry.get_queries_registered():
            self.__json_rpc_query_server.register(query, handler)

        self.__server_process = Process(target=self.__json_rpc_query_server.run, args=(self.__self_port,))
        self.__server_process.start()

    def execute(self, query: Query) -> QueryResponse:
        handler_address = self.__query_registry.get_query_destination_contact(query.__class__)
        if handler_address is None:
            raise HandlerNotFoundForQuery(query.__class__.__name__)

        return self.__execute_query(query, handler_address)

    def __execute_query(self, query: Query, query_handler_addr: str) -> QueryResponse:
        serialized_query = self.__query_serializer.serialize(query)

        request_response = requests.post(
            query_handler_addr, json=request(query.__class__.__name__, params=(serialized_query,))
        )
        json_rpc_response = to_result(request_response.json())

        if isinstance(json_rpc_response, Error):
            raise QueryExecutionFailed(query, json_rpc_response.message)
        return self.__query_response_deserializer.deserialize(json_rpc_response.result)

    def _stop(self) -> None:
        server_process = self.__server_process
        if server_process is not None and server_process.pid is not None:
            os.kill(server_process.pid, signal.SIGINT)
            server_process.join()
