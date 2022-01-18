from dataclasses import asdict
from json import dumps

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class PassengerJSONSerializer(PassengerSerializer):
    def serialize(self, passenger: Passenger) -> str:
        serialized_data = {
            "passenger_data": self.__get_passenger_data(passenger),
            "passenger_type": self.__get_passenger_type(passenger),
        }
        return dumps(serialized_data)

    def __get_passenger_data(self, passenger: Passenger) -> dict:
        return asdict(passenger)

    def __get_passenger_type(self, passenger: Passenger) -> str:
        return ".".join([passenger.__module__, passenger.__class__.__name__])
