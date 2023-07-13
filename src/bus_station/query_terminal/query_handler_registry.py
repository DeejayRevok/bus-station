from typing import Optional

from bus_station.bus_stop.registration.bus_stop_registry import BusStopRegistry
from bus_station.passengers.passenger_registry import passenger_bus_stop_registry
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.query_handler import QueryHandler


class QueryHandlerRegistry(BusStopRegistry[QueryHandler]):
    def get_handler_from_query(self, query_name: str) -> Optional[QueryHandler]:
        query_handler_names = passenger_bus_stop_registry.get_bus_stops_for_passenger(query_name)
        if len(query_handler_names) == 0:
            return None

        query_handler_name = next(iter(query_handler_names))
        query_handler = self.get_bus_stop_by_name(query_handler_name)

        if not isinstance(query_handler, QueryHandler):
            raise HandlerNotFoundForQuery(query_name)
        return query_handler
