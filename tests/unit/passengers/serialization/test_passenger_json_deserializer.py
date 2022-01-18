from dataclasses import dataclass
from unittest import TestCase

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.serialization.passenger_deserialization_error import PassengerDeserializationError
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer


@dataclass(frozen=True)
class TestPassenger(Passenger):
    test_arg: str


class TestPassengerJSONDeserializer(TestCase):
    def setUp(self) -> None:
        self.passenger_json_deserializer = PassengerJSONDeserializer()

    def test_deserialize_no_class(self):
        test_passenger_serialized = (
            '{"passenger_data": {"test_arg": "test"}, "passenger_type": "'
            + TestPassenger.__module__
            + "."
            + TestPassenger.__name__
            + '"}'
        )

        passenger_deserialized = self.passenger_json_deserializer.deserialize(test_passenger_serialized)

        expected_passenger_deserialized = TestPassenger(test_arg="test")
        self.assertEqual(expected_passenger_deserialized, passenger_deserialized)

    def test_deserialize_class_success(self):
        test_passenger_serialized = (
            '{"passenger_data": {"test_arg": "test"}, "passenger_type": "'
            + TestPassenger.__module__
            + "."
            + TestPassenger.__name__
            + '"}'
        )

        passenger_deserialized = self.passenger_json_deserializer.deserialize(test_passenger_serialized, TestPassenger)

        expected_passenger_deserialized = TestPassenger(test_arg="test")
        self.assertEqual(expected_passenger_deserialized, passenger_deserialized)

    def test_deserialize_class_error(self):
        test_passenger_serialized = (
            '{"passenger_data": {"test_arg_not_existent": "test"}, "passenger_type": "'
            + TestPassenger.__module__
            + "."
            + TestPassenger.__name__
            + '"}'
        )

        with self.assertRaises(PassengerDeserializationError) as pderr:
            self.passenger_json_deserializer.deserialize(test_passenger_serialized, TestPassenger)

            self.assertEqual(TestPassenger, pderr.passenger)
            self.assertEqual("Missing value for field test_arg", pderr.reason)
