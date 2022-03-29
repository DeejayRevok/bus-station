from typing import Any, Optional, Set, Type

from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.passengers.passenger_record.passenger_record import PassengerRecord
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.registry.query_registry import QueryRegistry
from bus_station.shared_terminal.bus_stop_resolver.bus_stop_resolver import BusStopResolver
from bus_station.shared_terminal.fqn_getter import FQNGetter


class InMemoryQueryRegistry(QueryRegistry):
    def __init__(
        self,
        in_memory_repository: InMemoryPassengerRecordRepository,
        fqn_getter: FQNGetter,
        query_handler_resolver: BusStopResolver[QueryHandler],
        passenger_class_resolver: PassengerClassResolver,
    ):
        self.__in_memory_repository = in_memory_repository
        self.__fqn_getter = fqn_getter
        self.__query_handler_resolver = query_handler_resolver
        self.__passenger_class_resolver = passenger_class_resolver

    def _register(self, query: Type[Query], handler: QueryHandler, handler_contact: Any) -> None:
        self.__in_memory_repository.save(
            PassengerRecord(
                passenger_name=query.__name__,
                passenger_fqn=self.__fqn_getter.get(query),
                destination_fqn=self.__fqn_getter.get(handler),
                destination_contact=handler_contact,
            )
        )

    def get_query_destination(self, query: Type[Query]) -> Optional[QueryHandler]:
        query_records = self.__in_memory_repository.find_by_passenger_name(query.__name__)
        if query_records is None:
            return None

        query_handler_fqn = query_records[0].destination_fqn
        return self.__query_handler_resolver.resolve_from_fqn(query_handler_fqn)

    def get_query_destination_contact(self, query: Type[Query]) -> Optional[Any]:
        query_records = self.__in_memory_repository.find_by_passenger_name(query.__name__)
        if query_records is None:
            return None
        return query_records[0].destination_contact

    def get_queries_registered(self) -> Set[Type[Query]]:
        queries_registered = set()
        for query_record in self.__in_memory_repository.all():
            query = self.__passenger_class_resolver.resolve_from_fqn(query_record.passenger_fqn)
            if query is None or not issubclass(query, Query):
                continue
            queries_registered.add(query)
        return queries_registered

    def unregister(self, query: Type[Query]) -> None:
        self.__in_memory_repository.delete_by_passenger_name(query.__name__)
