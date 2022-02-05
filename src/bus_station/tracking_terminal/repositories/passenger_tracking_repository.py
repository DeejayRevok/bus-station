from abc import abstractmethod
from typing import Generic, Optional, TypeVar

from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking

T = TypeVar("T", bound=PassengerTracking)


class PassengerTrackingRepository(Generic[T]):
    @abstractmethod
    def save(self, passenger_tracking: T) -> None:
        pass

    @abstractmethod
    def find_by_id(self, passenger_tracking_id: str) -> Optional[T]:
        pass
