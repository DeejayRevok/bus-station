from typing import Type, TypeVar

from bus_station.command_terminal.command import Command
from bus_station.event_terminal.event import Event
from bus_station.passengers.passenger import Passenger
from bus_station.query_terminal.query import Query
from bus_station.tracking_terminal.models.command_tracking import CommandTracking
from bus_station.tracking_terminal.models.event_tracking import EventTracking
from bus_station.tracking_terminal.models.query_tracking import QueryTracking

P = TypeVar("P", bound=Passenger)


class PassengerModelTrackingMap:
    def get_tracking_model(self, passenger: P) -> Type:
        match passenger:
            case Command():
                return CommandTracking
            case Event():
                return EventTracking
            case Query():
                return QueryTracking
            case _:
                raise NotImplementedError(f"Passenger of type {passenger.__class__} not supported")
