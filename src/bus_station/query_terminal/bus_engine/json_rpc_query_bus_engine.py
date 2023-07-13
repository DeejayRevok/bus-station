from bus_station.query_terminal.json_rpc_query_server import JsonRPCQueryServer
from bus_station.query_terminal.query_handler_not_found import QueryHandlerNotFound
from bus_station.query_terminal.query_handler_registry import QueryHandlerRegistry
from bus_station.shared_terminal.engine.engine import Engine


class JsonRPCQueryBusEngine(Engine):
    def __init__(
        self, server: JsonRPCQueryServer, query_handler_registry: QueryHandlerRegistry, query_handler_name: str
    ):
        super().__init__()
        self.__server = server
        self.__register_query_in_server(query_handler_registry, query_handler_name)

    def __register_query_in_server(self, query_handler_registry: QueryHandlerRegistry, query_handler_name: str) -> None:
        handler = query_handler_registry.get_bus_stop_by_name(query_handler_name)
        if handler is None:
            raise QueryHandlerNotFound(query_handler_name)

        query_type = handler.passenger()
        self.__server.register(query_type, handler)

    def start(self) -> None:
        self.__server.run()

    def stop(self):
        pass
