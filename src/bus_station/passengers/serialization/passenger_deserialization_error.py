from typing import Type

from bus_station.passengers.passenger import Passenger


class PassengerDeserializationError(Exception):
    def __init__(self, passenger: Type[Passenger], reason: str):
        self.reason = reason
        self.passenger = passenger
        super().__init__(f"Error deserializing {passenger.__name__}. Reason: {reason}")
