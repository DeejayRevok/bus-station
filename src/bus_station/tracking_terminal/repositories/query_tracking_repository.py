from abc import ABC

from bus_station.tracking_terminal.models.query_tracking import QueryTracking
from bus_station.tracking_terminal.repositories.passenger_tracking_repository import PassengerTrackingRepository


class QueryTrackingRepository(PassengerTrackingRepository[QueryTracking], ABC):
    pass
