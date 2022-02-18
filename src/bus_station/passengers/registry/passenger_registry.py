from abc import abstractmethod
from typing import Type, TypeVar, runtime_checkable, Iterable, Protocol, Optional

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.registry.destination_registration import DestinationRegistration
from bus_station.shared_terminal.bus_stop import BusStop

D = TypeVar("D", bound=BusStop)
C = TypeVar("C")


@runtime_checkable
class PassengerRegistry(Protocol[D, C]):

    @abstractmethod
    def register_destination(self, destination: D, destination_contact: C) -> None:
        pass

    @abstractmethod
    def get_passenger_destination_registration(self, passenger: Type[Passenger]) -> Optional[DestinationRegistration]:
        pass

    @abstractmethod
    def get_registered_passengers(self) -> Iterable[Type[Passenger]]:
        pass

    @abstractmethod
    def unregister(self, passenger: Type[Passenger]) -> None:
        pass

    @abstractmethod
    def _get_destination_passenger(self, destination: D) -> Type[Passenger]:
        pass

    def __contains__(self, passenger: Type[Passenger]) -> bool:
        passenger_destination = self.get_passenger_destination_registration(passenger)
        if passenger_destination is None or passenger_destination.destination_contact is None:
            return False
        return True
