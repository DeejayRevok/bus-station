from typing import Iterable, List, Optional

from redis import Redis

from bus_station.passengers.passenger_record.passenger_record import PassengerRecord
from bus_station.passengers.passenger_record.passenger_record_repository import PassengerRecordRepository


class RedisPassengerRecordRepository(PassengerRecordRepository):
    def __init__(self, client: Redis):
        self.__client = client

    def save(self, passenger_record: PassengerRecord[str]) -> None:
        str_passenger_record = str(passenger_record)
        self.__client.lpush(passenger_record.passenger_name, str_passenger_record.encode("UTF-8"))

    def find_by_passenger_name(self, passenger_name: str) -> Optional[List[PassengerRecord]]:
        redis_records = []
        for redis_value in self.__client.lrange(passenger_name, 0, -1):
            passenger_record = PassengerRecord.from_str(redis_value.decode("UTF-8"))
            redis_records.append(passenger_record)

        if len(redis_records) == 0:
            return None
        return redis_records

    def all(self) -> Iterable[PassengerRecord]:
        for passenger_name in self.__client.scan_iter("*"):
            passenger_records = self.find_by_passenger_name(passenger_name)
            if passenger_records is None:
                continue
            for passenger_record in passenger_records:
                yield passenger_record

    def delete_by_passenger_name(self, passenger_name: str) -> None:
        self.__client.delete(passenger_name)
