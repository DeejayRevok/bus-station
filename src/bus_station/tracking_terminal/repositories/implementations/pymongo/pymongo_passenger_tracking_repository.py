from abc import abstractmethod
from typing import Optional, Type

from pymongo.database import Database

from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking
from bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_deserializer import (
    MongoPassengerTrackingDeserializer,
)
from bus_station.tracking_terminal.repositories.implementations.pymongo.mongo_passenger_tracking_serializer import (
    MongoPassengerTrackingSerializer,
)
from bus_station.tracking_terminal.repositories.passenger_tracking_repository import PassengerTrackingRepository


class PyMongoPassengerTrackingRepository(PassengerTrackingRepository):
    def __init__(
        self,
        py_mongo_db: Database,
        mongo_tracking_serializer: MongoPassengerTrackingSerializer,
        mongo_tracking_deserializer: MongoPassengerTrackingDeserializer,
    ):
        self.__collection = py_mongo_db.get_collection(self._collection)
        self.__serializer = mongo_tracking_serializer
        self.__deserializer = mongo_tracking_deserializer

    @property
    def model(self) -> Type[PassengerTracking]:
        return PassengerTracking

    @property
    @abstractmethod
    def _collection(self) -> str:
        pass

    def save(self, passenger_tracking: PassengerTracking) -> None:
        serialized_passenger_tracking = self.__serializer.serialize(passenger_tracking)
        self.__collection.update_one(
            filter={"_id": passenger_tracking.id}, update={"$set": serialized_passenger_tracking}, upsert=True
        )

    def find_by_id(self, passenger_tracking_id: str) -> Optional[PassengerTracking]:
        serialized_passenger_tracking = self.__collection.find_one(filter={"_id": passenger_tracking_id})
        if serialized_passenger_tracking is None:
            return None
        return self.__deserializer.deserialize(serialized_passenger_tracking, self.model)
