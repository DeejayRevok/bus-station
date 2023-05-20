from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
from typing import Any

from bus_station.bus_stop.bus_stop import BusStop
from bus_station.passengers.passenger import Passenger
from bus_station.tracking_terminal.models.passenger_model_tracking_map import PassengerModelTrackingMap
from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking


class PassengerTracker(ABC):
    def __init__(self, passenger_model_tracking_map: PassengerModelTrackingMap):
        self.__passenger_model_tracking_map = passenger_model_tracking_map

    def start_tracking(self, passenger: Passenger, bus_stop: BusStop) -> None:
        tracking_model = self.__passenger_model_tracking_map.get_tracking_model(passenger)
        tracking = tracking_model(
            passenger_id=passenger.passenger_id,
            root_passenger_id=passenger.root_passenger_id,
            name=passenger.passenger_name(),
            executor_name=bus_stop.bus_stop_name(),
            data=self.__get_passenger_data(passenger),
            execution_start=datetime.now(),
            execution_end=None,
            success=None,
        )
        self._track(tracking)

    @abstractmethod
    def _track(self, passenger_tracking: PassengerTracking) -> None:
        pass

    def end_tracking(self, passenger: Passenger, bus_stop: BusStop, success: bool, **track_data: Any) -> None:
        tracking_model = self.__passenger_model_tracking_map.get_tracking_model(passenger)
        tracking = tracking_model(
            passenger_id=passenger.passenger_id,
            root_passenger_id=passenger.root_passenger_id,
            name=passenger.passenger_name(),
            executor_name=bus_stop.bus_stop_name(),
            data=self.__get_passenger_data(passenger),
            execution_start=None,
            execution_end=datetime.now(),
            success=success,
        )
        self.__set_track_data(tracking, **track_data)
        self._track(tracking)

    def __get_passenger_data(self, passenger: Passenger) -> dict:
        passenger_data = asdict(passenger)
        del passenger_data["passenger_id"]
        del passenger_data["root_passenger_id"]
        return passenger_data

    def __set_track_data(self, passenger_tracking: PassengerTracking, **track_data: Any) -> None:
        for track_data_key, track_data_value in track_data.items():
            setattr(passenger_tracking, track_data_key, track_data_value)
