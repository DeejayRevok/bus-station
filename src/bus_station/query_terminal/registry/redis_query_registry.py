from typing import Iterable, List, Optional, Tuple, Type

from bus_station.passengers.registry.passenger_record import PassengerRecord
from bus_station.passengers.registry.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.registry.remote_query_registry import RemoteQueryRegistry


class RedisQueryRegistry(RemoteQueryRegistry):
    def __init__(self, redis_repository: RedisPassengerRecordRepository):
        self.__redis_repository = redis_repository

    def _register(self, query: Type[Query], handler: QueryHandler, handler_contact: str) -> None:
        self.__redis_repository.save(
            PassengerRecord(passenger=query, destination=handler, destination_contact=handler_contact)
        )

    def get_query_destination_contact(self, query: Type[Query]) -> Optional[str]:
        query_records = self.__redis_repository.filter_by_passenger(query)
        if query_records is None:
            return None
        return query_records[0].destination_contact

    def get_queries_registered(self) -> Iterable[Tuple[Type[Query], QueryHandler, str]]:
        for query_records in self.__redis_repository.all():
            query_record = query_records[0]
            yield query_record.passenger, query_record.destination, query_record.destination_contact

    def get_query_destination(self, query: Type[Query]) -> Optional[QueryHandler]:
        query_records: Optional[
            List[PassengerRecord[Query, QueryHandler]]
        ] = self.__redis_repository.filter_by_passenger(query)
        if query_records is None:
            return None
        return query_records[0].destination

    def unregister(self, query: Type[Query]) -> None:
        self.__redis_repository.delete_by_passenger(query)
