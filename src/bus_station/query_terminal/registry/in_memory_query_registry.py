from typing import Any, Iterable, List, Optional, Tuple, Type

from bus_station.passengers.registry.in_memory_passenger_record_repository import InMemoryPassengerRecordRepository
from bus_station.passengers.registry.passenger_record import PassengerRecord
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.registry.query_registry import QueryRegistry


class InMemoryQueryRegistry(QueryRegistry):
    def __init__(self, in_memory_repository: InMemoryPassengerRecordRepository):
        self.__in_memory_repository = in_memory_repository

    def _register(self, query: Type[Query], handler: QueryHandler, handler_contact: Any) -> None:
        self.__in_memory_repository.save(
            PassengerRecord(passenger=query, destination=handler, destination_contact=handler_contact)
        )

    def get_query_destination(self, query: Type[Query]) -> Optional[QueryHandler]:
        query_records: Optional[
            List[PassengerRecord[Query, QueryHandler]]
        ] = self.__in_memory_repository.filter_by_passenger(query)
        if query_records is None:
            return None
        return query_records[0].destination

    def get_query_destination_contact(self, query: Type[Query]) -> Optional[Any]:
        query_records = self.__in_memory_repository.filter_by_passenger(query)
        if query_records is None:
            return None
        return query_records[0].destination_contact

    def get_queries_registered(self) -> Iterable[Tuple[Type[Query], QueryHandler, Any]]:
        for query_records in self.__in_memory_repository.all():
            query_record = query_records[0]
            yield query_record.passenger, query_record.destination, query_record.destination_contact

    def unregister(self, query: Type[Query]) -> None:
        self.__in_memory_repository.delete_by_passenger(query)
