from functools import partial
from typing import Optional

from bus_station.bus_stop.registration.bus_stop_registry import BusStopRegistry
from bus_station.bus_stop.resolvers.bus_stop_resolver import BusStopResolver
from bus_station.passengers.passenger_registry import passenger_bus_stop_registry
from bus_station.passengers.passenger_resolvers import resolve_passenger_class_from_bus_stop
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.query_handler import QueryHandler


class QueryHandlerRegistry(BusStopRegistry[QueryHandler]):
    def __init__(
        self,
        bus_stop_resolver: BusStopResolver,
    ):
        bus_stop_passenger_resolver = partial(
            resolve_passenger_class_from_bus_stop,
            bus_stop_handle_function_name="handle",
            passenger_type_name="query",
        )
        super().__init__(bus_stop_resolver, bus_stop_passenger_resolver)

    def get_handler_from_query(self, query_name: str) -> Optional[QueryHandler]:
        query_handler_ids = passenger_bus_stop_registry.get_bus_stops_for_passenger(query_name)
        if len(query_handler_ids) == 0:
            return None

        query_handler_id = next(iter(query_handler_ids))
        resolved_query_handler = self._bus_stop_resolver.resolve(query_handler_id)

        if not isinstance(resolved_query_handler, QueryHandler):
            raise HandlerNotFoundForQuery(query_name)
        return resolved_query_handler
