from typing import Any, Optional, Set, Type

from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.passengers.passenger_record.passenger_record import PassengerRecord
from bus_station.passengers.passenger_resolvers import resolve_passenger_class_from_fqn
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.registry.query_registry import QueryRegistry
from bus_station.shared_terminal.bus_stop_resolver.bus_stop_resolver import BusStopResolver
from bus_station.shared_terminal.fqn import resolve_fqn


class InMemoryQueryRegistry(QueryRegistry):
    def __init__(
        self,
        in_memory_repository: InMemoryPassengerRecordRepository,
        query_handler_resolver: BusStopResolver[QueryHandler],
    ):
        self.__in_memory_repository = in_memory_repository
        self.__query_handler_resolver = query_handler_resolver

    def _register(self, query: Type[Query], handler: QueryHandler, handler_contact: Any) -> None:
        self.__in_memory_repository.save(
            PassengerRecord(
                passenger_name=query.passenger_name(),
                passenger_fqn=resolve_fqn(query),
                destination_name=handler.bus_stop_name(),
                destination_fqn=resolve_fqn(handler),
                destination_contact=handler_contact,
            )
        )

    def get_query_destination(self, query_name: str) -> Optional[QueryHandler]:
        query_records = self.__in_memory_repository.find_by_passenger_name(query_name)
        if query_records is None:
            return None

        query_handler_fqn = query_records[0].destination_fqn
        return self.__query_handler_resolver.resolve_from_fqn(query_handler_fqn)

    def get_query_destination_contact(self, query_name: str) -> Optional[Any]:
        query_records = self.__in_memory_repository.find_by_passenger_name(query_name)
        if query_records is None:
            return None
        return query_records[0].destination_contact

    def get_queries_registered(self) -> Set[Type[Query]]:
        queries_registered = set()
        for query_record in self.__in_memory_repository.all():
            query = resolve_passenger_class_from_fqn(query_record.passenger_fqn)
            if query is None or not issubclass(query, Query):
                continue
            queries_registered.add(query)
        return queries_registered

    def unregister(self, query_name: str) -> None:
        self.__in_memory_repository.delete_by_passenger_name(query_name)
