from typing import Optional, Type, TypeVar

from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.json_rpc_query_server import JsonRPCQueryServer
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.registry.query_registry import QueryRegistry
from bus_station.shared_terminal.engine.engine import Engine

Q = TypeVar("Q", bound=Query)


class JsonRPCQueryBusEngine(Engine):
    def __init__(self, server: JsonRPCQueryServer, query_registry: QueryRegistry, query_type: Optional[Type[Q]] = None):
        super().__init__()
        self.__server = server
        if query_type is not None:
            self.__register_query_in_server(query_registry, query_type)
            return

        for command_type in query_registry.get_queries_registered():
            self.__register_query_in_server(query_registry, command_type)

    def __register_query_in_server(self, query_registry: QueryRegistry, query_type: Type[Q]) -> None:
        handler = query_registry.get_query_destination(query_type)
        if handler is None:
            raise HandlerNotFoundForQuery(query_type.__name__)
        self.__server.register(query_type, handler)

    def start(self) -> None:
        self.__server.run()

    def stop(self):
        pass
