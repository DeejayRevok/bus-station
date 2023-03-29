from dataclasses import dataclass
from unittest import TestCase
from uuid import uuid4

from bus_station.passengers.passenger import Passenger


@dataclass(frozen=True)
class PassengerTest(Passenger):
    first_property: str
    second_property: int

    @classmethod
    def passenger_name(cls) -> str:
        return "test"


class TestPassenger(TestCase):
    def test_from_data_dict(self):
        test_uuid = str(uuid4())
        test_root_passenger_id = str(uuid4())
        data_dict = {
            "passenger_id": test_uuid,
            "root_passenger_id": test_root_passenger_id,
            "first_property": "test_first_property",
            "second_property": 4,
        }

        result_passenger = PassengerTest.from_data_dict(data_dict)

        expected_passenger = PassengerTest(first_property="test_first_property", second_property=4)
        object.__setattr__(expected_passenger, "passenger_id", test_uuid)
        object.__setattr__(expected_passenger, "root_passenger_id", test_root_passenger_id)
        self.assertEqual(expected_passenger, result_passenger)

    def test_from_data_dict_missing_field(self):
        test_uuid = str(uuid4())
        test_root_passenger_id = str(uuid4())
        data_dict = {"passenger_id": test_uuid, "root_passenger_id": test_root_passenger_id, "second_property": 4}

        with self.assertRaises(ValueError):
            PassengerTest.from_data_dict(data_dict)
