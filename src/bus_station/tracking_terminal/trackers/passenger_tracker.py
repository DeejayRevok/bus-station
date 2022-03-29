from dataclasses import asdict
from datetime import datetime
from typing import Any, Type

from bus_station.passengers.passenger import Passenger
from bus_station.shared_terminal.bus_stop import BusStop
from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking
from bus_station.tracking_terminal.repositories.passenger_tracking_repository import PassengerTrackingRepository
from bus_station.tracking_terminal.trackers.passenger_tracking_not_found import PassengerTrackingNotFound


class PassengerTracker:
    def __init__(self, passenger_tracking_repository: PassengerTrackingRepository):
        self.__repository = passenger_tracking_repository

    def _get_tracking_model(self, passenger: Passenger) -> Type:
        return PassengerTracking

    def start_tracking(self, passenger: Passenger, bus_stop: BusStop) -> None:
        tracking_model = self._get_tracking_model(passenger)
        tracking = tracking_model(
            id=str(id(passenger)),
            name=passenger.__class__.__name__,
            executor_name=bus_stop.__class__.__name__,
            data=asdict(passenger),
            execution_start=datetime.now(),
            execution_end=None,
        )
        self.__repository.save(tracking)

    def end_tracking(self, passenger: Passenger, **track_data: Any) -> None:
        passenger_id = str(id(passenger))
        tracking = self.__repository.find_by_id(passenger_id)
        if tracking is None:
            raise PassengerTrackingNotFound(passenger.__class__.__name__, passenger_id)
        tracking.execution_end = datetime.now()
        self.__set_track_data(tracking, **track_data)
        self.__repository.save(tracking)

    def __set_track_data(self, passenger_tracking: PassengerTracking, **track_data: Any) -> None:
        for track_data_key, track_data_value in track_data.items():
            setattr(passenger_tracking, track_data_key, track_data_value)
