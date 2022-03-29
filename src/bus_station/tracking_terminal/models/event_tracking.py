from dataclasses import dataclass

from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking


@dataclass
class EventTracking(PassengerTracking):
    pass
