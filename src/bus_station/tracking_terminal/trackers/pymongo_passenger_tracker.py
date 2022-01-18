from typing import Type

from bus_station.passengers.passenger import Passenger
from bus_station.tracking_terminal.repositories.implementations.pymongo.pymongo_passenger_tracking_repository import (
    PyMongoPassengerTrackingRepository,
)
from bus_station.tracking_terminal.trackers.passenger_tracker import PassengerTracker


class PyMongoPassengerTracker(PassengerTracker):
    def __init__(self, passenger_tracking_repository: PyMongoPassengerTrackingRepository):
        super().__init__(passenger_tracking_repository)
        self.tracking_model = passenger_tracking_repository.model

    def _get_tracking_model(self, passenger: Passenger) -> Type:
        return self.tracking_model
