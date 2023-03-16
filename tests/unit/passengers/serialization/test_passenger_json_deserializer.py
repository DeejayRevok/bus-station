from dataclasses import dataclass
from unittest import TestCase
from uuid import uuid4

from bus_station.passengers.passenger import Passenger
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer


@dataclass(frozen=True)
class TestPassenger(Passenger):
    test_arg: str

    @classmethod
    def passenger_name(cls) -> str:
        return "passenger.test_passenger"


class TestPassengerJSONDeserializer(TestCase):
    def setUp(self) -> None:
        self.passenger_json_deserializer = PassengerJSONDeserializer()

    def test_deserialize_no_class(self):
        passenger_id = str(uuid4())
        test_passenger_serialized = (
            '{"passenger_data": {'
            + '"passenger_id":"'
            + passenger_id
            + '",'
            + '"test_arg": "test"}, "passenger_type": "'
            + TestPassenger.__module__
            + "."
            + TestPassenger.__name__
            + '"}'
        )

        passenger_deserialized = self.passenger_json_deserializer.deserialize(test_passenger_serialized)

        expected_passenger_deserialized = TestPassenger(test_arg="test")
        object.__setattr__(expected_passenger_deserialized, "passenger_id", passenger_id)
        self.assertEqual(expected_passenger_deserialized, passenger_deserialized)

    def test_deserialize_class_success(self):
        passenger_id = str(uuid4())
        test_passenger_serialized = (
            '{"passenger_data": {'
            + '"passenger_id":"'
            + passenger_id
            + '",'
            + '"test_arg": "test"}, "passenger_type": "'
            + TestPassenger.__module__
            + "."
            + TestPassenger.__name__
            + '"}'
        )

        passenger_deserialized = self.passenger_json_deserializer.deserialize(test_passenger_serialized, TestPassenger)

        expected_passenger_deserialized = TestPassenger(test_arg="test")
        object.__setattr__(expected_passenger_deserialized, "passenger_id", passenger_id)
        self.assertEqual(expected_passenger_deserialized, passenger_deserialized)

    def test_deserialize_class_error(self):
        test_passenger_serialized = (
            '{"passenger_data": {'
            + '"passenger_id":"'
            + str(uuid4())
            + '",'
            + '"test_arg_not_existent": "test"}, "passenger_type": "'
            + TestPassenger.__module__
            + "."
            + TestPassenger.__name__
            + '"}'
        )

        with self.assertRaises(ValueError) as context:
            self.passenger_json_deserializer.deserialize(test_passenger_serialized, TestPassenger)

        self.assertEqual("Missing value for field test_arg when recreating TestPassenger", str(context.exception))
