from abc import ABC, abstractmethod
from dataclasses import MISSING, Field, dataclass, field, fields
from typing import Optional
from uuid import uuid4

from typing_extensions import Self


@dataclass(frozen=True)
class Passenger(ABC):
    passenger_id: str = field(init=False, default_factory=lambda: str(uuid4()))
    root_passenger_id: Optional[str] = field(init=False, default_factory=lambda: None)

    @classmethod
    @abstractmethod
    def passenger_name(cls) -> str:
        pass

    @classmethod
    def from_data_dict(cls, passenger_data: dict) -> Self:
        passenger_data_copy = passenger_data.copy()
        passenger_id = cls.__get_passenger_id(passenger_data_copy)
        root_passenger_id = cls.__get_root_passenger_id(passenger_data_copy)

        passenger = cls.__from_data_dict(passenger_data_copy)

        object.__setattr__(passenger, "passenger_id", passenger_id)
        if root_passenger_id is not None:
            passenger.set_root_passenger_id(root_passenger_id)

        return passenger

    def set_root_passenger_id(self, root_passenger_id: Optional[str]) -> None:
        object.__setattr__(self, "root_passenger_id", root_passenger_id)

    @classmethod
    def __get_passenger_id(cls, passenger_data: dict) -> str:
        return passenger_data.pop("passenger_id")

    @classmethod
    def __get_root_passenger_id(cls, passenger_data: dict) -> Optional[str]:
        if "root_passenger_id" not in passenger_data:
            return None
        return passenger_data.pop("root_passenger_id")

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
