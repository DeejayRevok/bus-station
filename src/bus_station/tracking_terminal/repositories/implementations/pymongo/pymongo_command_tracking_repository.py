from typing import Type

from bus_station.tracking_terminal.models.command_tracking import CommandTracking
from bus_station.tracking_terminal.repositories.command_tracking_repository import CommandTrackingRepository
from bus_station.tracking_terminal.repositories.implementations.pymongo.pymongo_passenger_tracking_repository import (
    PyMongoPassengerTrackingRepository,
)


class PyMongoCommandTrackingRepository(PyMongoPassengerTrackingRepository, CommandTrackingRepository):
    @property
    def model(self) -> Type[CommandTracking]:
        return CommandTracking

    @property
    def _collection(self) -> str:
        return "command_tracking"
