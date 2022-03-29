from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Generic, TypeVar

C = TypeVar("C")


@dataclass(frozen=True)
class PassengerRecord(Generic[C]):
    __STR_SEPARATOR: ClassVar[str] = "-"
    __STR_PATTERN: ClassVar[
        str
    ] = "{passenger_name}{separator}{passenger_fqn}{separator}{destination_fqn}{separator}{destination_contact}"

    passenger_name: str
    passenger_fqn: str
    destination_fqn: str
    destination_contact: C

    @classmethod
    def from_str(cls, passenger_record_str: str) -> PassengerRecord[str]:
        passenger_record_attrs = passenger_record_str.split(sep=cls.__STR_SEPARATOR)
        if len(passenger_record_attrs) > 4:
            raise ValueError(
                f"Passenger record string {passenger_record_str} is not a valid representation of PassengerRecord"
            )

        return cls[str](
            passenger_name=passenger_record_attrs[0],
            passenger_fqn=passenger_record_attrs[1],
            destination_fqn=passenger_record_attrs[2],
            destination_contact=passenger_record_attrs[3],
        )

    def __str__(self) -> str:
        destination_contact = self.destination_contact
        if not isinstance(destination_contact, str):
            destination_contact = str(destination_contact)
        return self.__STR_PATTERN.format(
            passenger_name=self.passenger_name,
            separator=self.__STR_SEPARATOR,
            passenger_fqn=self.passenger_fqn,
            destination_fqn=self.destination_fqn,
            destination_contact=destination_contact,
        )
