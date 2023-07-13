from bus_station.query_terminal.query_handler_not_found import QueryHandlerNotFound
from bus_station.query_terminal.query_handler_registry import QueryHandlerRegistry
from bus_station.shared_terminal.engine.engine import Engine
from bus_station.shared_terminal.rpyc_server import RPyCServer


class RPyCQueryBusEngine(Engine):
    def __init__(self, rpyc_server: RPyCServer, query_handler_registry: QueryHandlerRegistry, query_handler_name: str):
        super().__init__()
        self.__server = rpyc_server
        self.__register_query_in_server(query_handler_registry, query_handler_name)

    def __register_query_in_server(self, query_handler_registry: QueryHandlerRegistry, query_handler_name: str) -> None:
        handler = query_handler_registry.get_bus_stop_by_name(query_handler_name)
        if handler is None:
            raise QueryHandlerNotFound(query_handler_name)

        query_type = handler.passenger()
        self.__server.register(query_type, handler)

    def start(self) -> None:
        self.__server.run()

    def stop(self) -> None:
        pass
