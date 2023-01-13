from bus_station.passengers.resolve_passenger_from_bus_stop import resolve_passenger_from_bus_stop
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.json_rpc_query_server import JsonRPCQueryServer
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.registry.query_registry import QueryRegistry
from bus_station.shared_terminal.engine.engine import Engine


class JsonRPCQueryBusEngine(Engine):
    def __init__(self, server: JsonRPCQueryServer, query_registry: QueryRegistry, query_name: str):
        super().__init__()
        self.__server = server
        self.__register_query_in_server(query_registry, query_name)

    def __register_query_in_server(self, query_registry: QueryRegistry, query_name: str) -> None:
        handler = query_registry.get_query_destination(query_name)
        if handler is None:
            raise HandlerNotFoundForQuery(query_name)
        query_type = resolve_passenger_from_bus_stop(handler, "handle", "query", Query)
        self.__server.register(query_type, handler)

    def start(self) -> None:
        self.__server.run()

    def stop(self):
        pass
