from abc import ABC, abstractmethod
from dataclasses import MISSING, Field, dataclass, field, fields
from uuid import uuid4

from typing_extensions import Self


@dataclass(frozen=True)
class Passenger(ABC):
    passenger_id: str = field(init=False, default_factory=lambda: str(uuid4()))

    @classmethod
    @abstractmethod
    def passenger_name(cls) -> str:
        pass

    @classmethod
    def from_data_dict(cls, passenger_data: dict) -> Self:
        passenger_id = cls.__get_passenger_id(passenger_data)

        passenger = cls.__from_data_dict(passenger_data)

        object.__setattr__(passenger, "passenger_id", passenger_id)
        return passenger

    @classmethod
    def __get_passenger_id(cls, passenger_data: dict) -> str:
        return passenger_data.pop("passenger_id")

    @classmethod
    def __from_data_dict(cls, passenger_data: dict) -> Self:
        passenger_cls_field_values = {}
        for passenger_field in fields(cls):
            if cls.__is_field_required(passenger_field) and passenger_field.name not in passenger_data:
                raise ValueError(f"Missing value for field {passenger_field.name} when recreating {cls.__name__}")
            if passenger_field.name not in passenger_data:
                continue
            passenger_cls_field_values[passenger_field.name] = passenger_data[passenger_field.name]
        return cls(**passenger_cls_field_values)

    @classmethod
    def __is_field_required(cls, passenger_field: Field) -> bool:
        return passenger_field.default is MISSING and passenger_field.init is True
