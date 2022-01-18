from dataclasses import dataclass

from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking


@dataclass
class CommandTracking(PassengerTracking):
    pass
