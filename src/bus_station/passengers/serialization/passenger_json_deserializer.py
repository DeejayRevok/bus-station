from importlib import import_module
from json import loads
from typing import Generic, Optional, Type, TypeVar

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer

P = TypeVar("P", bound=Passenger)


class PassengerJSONDeserializer(PassengerDeserializer, Generic[P]):
    def deserialize(self, passenger_serialized: str, passenger_cls: Optional[Type[P]] = None) -> P:
        deserialized_data = loads(passenger_serialized)
        if passenger_cls is None:
            passenger_cls = self.__get_passenger_dataclass(deserialized_data)

        return passenger_cls.from_data_dict(deserialized_data["passenger_data"])

    def __get_passenger_dataclass(self, passenger_dict: dict) -> Type[P]:
        passenger_type = passenger_dict["passenger_type"]
        passenger_module_name, passenger_class_name = passenger_type.rsplit(".", 1)
        return getattr(import_module(passenger_module_name), passenger_class_name)
