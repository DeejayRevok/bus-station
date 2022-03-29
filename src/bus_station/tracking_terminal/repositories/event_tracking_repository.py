from abc import ABC

from bus_station.tracking_terminal.models.event_tracking import EventTracking
from bus_station.tracking_terminal.repositories.passenger_tracking_repository import PassengerTrackingRepository


class EventTrackingRepository(PassengerTrackingRepository[EventTracking], ABC):
    pass
