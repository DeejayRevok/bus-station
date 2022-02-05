from dataclasses import MISSING, Field, fields
from importlib import import_module
from json import loads
from typing import Generic, Optional, Type, TypeVar

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.serialization.passenger_deserialization_error import PassengerDeserializationError
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer

P = TypeVar("P", bound=Passenger)


class PassengerJSONDeserializer(PassengerDeserializer, Generic[P]):
    def deserialize(self, passenger_serialized: str, passenger_cls: Optional[Type[P]] = None) -> P:
        deserialized_data = loads(passenger_serialized)
        if passenger_cls is None:
            passenger_cls = self.__get_passenger_dataclass(deserialized_data)
        return self.__from_passenger_cls(passenger_cls, deserialized_data["passenger_data"])

    def __get_passenger_dataclass(self, passenger_dict: dict) -> Type[P]:
        passenger_type = passenger_dict["passenger_type"]
        passenger_module_name, passenger_class_name = passenger_type.rsplit(".", 1)
        return getattr(import_module(passenger_module_name), passenger_class_name)

    def __from_passenger_cls(self, passenger_cls: Type[P], passenger_data: dict) -> P:
        passenger_cls_field_values = dict()
        for passenger_field in fields(passenger_cls):
            passenger_field: Field = passenger_field
            if passenger_field.default is MISSING and passenger_field.name not in passenger_data:
                raise PassengerDeserializationError(passenger_cls, f"Missing value for field {passenger_field.name}")
            if passenger_field.name not in passenger_data:
                continue
            passenger_cls_field_values[passenger_field.name] = passenger_data[passenger_field.name]
        return passenger_cls(**passenger_cls_field_values)
