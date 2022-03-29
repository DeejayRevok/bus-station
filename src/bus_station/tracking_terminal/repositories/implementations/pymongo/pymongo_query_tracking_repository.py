from typing import Type

from bus_station.tracking_terminal.models.query_tracking import QueryTracking
from bus_station.tracking_terminal.repositories.implementations.pymongo.pymongo_passenger_tracking_repository import (
    PyMongoPassengerTrackingRepository,
)
from bus_station.tracking_terminal.repositories.query_tracking_repository import QueryTrackingRepository


class PyMongoQueryTrackingRepository(PyMongoPassengerTrackingRepository, QueryTrackingRepository):
    @property
    def model(self) -> Type[QueryTracking]:
        return QueryTracking

    @property
    def _collection(self) -> str:
        return "query_tracking"
