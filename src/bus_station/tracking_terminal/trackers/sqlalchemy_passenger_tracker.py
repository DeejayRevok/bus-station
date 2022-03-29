from typing import Type

from bus_station.passengers.passenger import Passenger
from bus_station.tracking_terminal.mappers.sqlalchemy.sqlalchemy_mapper import SQLAlchemyMapper
from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking
from bus_station.tracking_terminal.repositories.passenger_tracking_repository import PassengerTrackingRepository
from bus_station.tracking_terminal.trackers.passenger_tracker import PassengerTracker


class SQLAlchemyPassengerTracker(PassengerTracker):
    def __init__(self, passenger_tracking_repository: PassengerTrackingRepository, sqlalchemy_mapper: SQLAlchemyMapper):
        super().__init__(passenger_tracking_repository)
        self.__sqlalchemy_mapper = sqlalchemy_mapper

    def _get_tracking_model(self, passenger: Passenger) -> Type:
        tracking_model = self.__sqlalchemy_mapper.model
        if tracking_model != PassengerTracking and not issubclass(tracking_model, PassengerTracking):
            raise TypeError("Mapped tracking model is not an instance of PassengerTracking")
        return tracking_model
