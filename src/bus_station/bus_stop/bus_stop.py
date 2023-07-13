from abc import ABC, abstractmethod
from typing import Callable, Type, TypeVar, get_type_hints

from bus_station.passengers.passenger import Passenger

PT = TypeVar("PT", bound=Passenger)


class BusStop(ABC):
    @classmethod
    @abstractmethod
    def bus_stop_name(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def passenger(cls) -> Type[Passenger]:
        pass

    @classmethod
    def _get_passenger_from_handling_method(
        cls, passenger_handling_method: Callable, passenger_argument_name: str
    ) -> Type[PT]:  # pyre-ignore [34]
        bus_stop_handle_typing = get_type_hints(passenger_handling_method)

        if passenger_argument_name not in bus_stop_handle_typing:
            raise TypeError(
                f"{passenger_handling_method.__name__} {passenger_argument_name} not found for {cls.bus_stop_name()}"
            )

        return bus_stop_handle_typing[passenger_argument_name]
