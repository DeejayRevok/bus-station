from abc import abstractmethod
from typing import Protocol

from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking


class PassengerTrackingSerializer(Protocol):
    @abstractmethod
    def serialize(self, passenger_tracking: PassengerTracking) -> str:
        pass
