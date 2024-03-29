from dataclasses import dataclass
from unittest import TestCase

from bus_station.command_terminal.command import Command
from bus_station.passengers.passenger_mapper import passenger_mapper
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer


@dataclass(frozen=True)
class TestPassenger:
    test_field1: str
    test_field2: int


class TestPassengerJSONSerializerMapped(TestCase):
    def setUp(self) -> None:
        passenger_mapper(TestPassenger, Command, "test_passenger_name")
        self.passenger_json_serializer = PassengerJSONSerializer()

    def test_serialize(self):
        test_passenger = TestPassenger(test_field1="test_field1_value", test_field2=22)
        test_passenger_type = TestPassenger.__module__ + "." + TestPassenger.__name__

        serialized_passenger = self.passenger_json_serializer.serialize(test_passenger)

        expected_serialized_passenger = (
            '{"passenger_data": {"test_field1": "test_field1_value", "test_field2": 22, "passenger_id": "'
            + test_passenger.passenger_id
            + '", "root_passenger_id": null}, '
            '"passenger_type": "' + test_passenger_type + '", "passenger_name": "test_passenger_name"}'
        )
        self.assertEqual(expected_serialized_passenger, serialized_passenger)
