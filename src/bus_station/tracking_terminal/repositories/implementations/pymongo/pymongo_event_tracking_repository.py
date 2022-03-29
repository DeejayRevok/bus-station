from typing import Type

from bus_station.tracking_terminal.models.event_tracking import EventTracking
from bus_station.tracking_terminal.repositories.event_tracking_repository import EventTrackingRepository
from bus_station.tracking_terminal.repositories.implementations.pymongo.pymongo_passenger_tracking_repository import (
    PyMongoPassengerTrackingRepository,
)


class PyMongoEventTrackingRepository(PyMongoPassengerTrackingRepository, EventTrackingRepository):
    @property
    def model(self) -> Type[EventTracking]:
        return EventTracking

    @property
    def _collection(self) -> str:
        return "event_tracking"
