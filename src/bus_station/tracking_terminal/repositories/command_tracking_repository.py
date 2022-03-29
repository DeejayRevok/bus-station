from abc import ABC

from bus_station.tracking_terminal.models.command_tracking import CommandTracking
from bus_station.tracking_terminal.repositories.passenger_tracking_repository import PassengerTrackingRepository


class CommandTrackingRepository(PassengerTrackingRepository[CommandTracking], ABC):
    pass
