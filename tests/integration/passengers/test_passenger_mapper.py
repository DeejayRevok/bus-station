from dataclasses import asdict, dataclass, field
from unittest import TestCase
from uuid import uuid4

from bus_station.command_terminal.command import Command
from bus_station.passengers.passenger_mapper import passenger_mapper


@dataclass(frozen=True)
class Dataclass:
    test_str_field: str
    test_int_field: int
    test_kwarg_default_field: str = field(default="test_kwarg_default_field")
    test_kwarg_default_factory_field: str = field(default_factory=lambda: str(uuid4()))


class TestPassengerMapper(TestCase):
    __passenger_data_dict = {
        "passenger_id": str(uuid4()),
        "root_passenger_id": str(uuid4()),
        "test_str_field": "test_str_field_data",
        "test_int_field": 2,
        "test_kwarg_default_field": "test_kwarg_default_field_data",
        "test_kwarg_default_factory_field": "test_kwarg_default_factory_field_data",
    }

    def test_passenger_mapper_non_dataclass(self):
        class NonDataclass:
            pass

        with self.assertRaises(ValueError):
            passenger_mapper(NonDataclass, Command)

    def test_passenger_mapper_dataclass(self):
        passenger_mapper(Dataclass, Command, "test_passenger")

        dataclass_instance = Dataclass(test_str_field="test_str_field", test_int_field=1)
        self.assertEqual(dataclass_instance.passenger_name(), "test_passenger")
        self.__assert_dataclass_members(dataclass_instance, "test_str_field", 1)
        self.__assert_passenger_base_members(dataclass_instance)
        dataclass_dict_instance = Dataclass.from_data_dict(self.__passenger_data_dict)
        self.assertIsInstance(dataclass_dict_instance, Dataclass)
        self.__assert_passenger_data_dict_members(dataclass_dict_instance)
        dataclass_dict = asdict(dataclass_dict_instance)
        self.assertEqual(dataclass_dict, self.__passenger_data_dict)

    def __assert_dataclass_members(self, dataclass_instance, test_str_field, test_int_field) -> None:
        self.assertEqual(dataclass_instance.test_str_field, test_str_field)
        self.assertEqual(dataclass_instance.test_int_field, test_int_field)
        self.assertEqual(dataclass_instance.test_kwarg_default_field, "test_kwarg_default_field")
        self.assertIsInstance(dataclass_instance.test_kwarg_default_factory_field, str)

    def __assert_passenger_base_members(self, dataclass_instance) -> None:
        self.assertIsNotNone(dataclass_instance.passenger_id)
        self.assertIsInstance(dataclass_instance.passenger_id, str)
        self.assertIsNone(dataclass_instance.root_passenger_id)

    def __assert_passenger_data_dict_members(self, passenger_data_dict_instance) -> None:
        self.assertEqual(passenger_data_dict_instance.test_str_field, self.__passenger_data_dict["test_str_field"])
        self.assertEqual(passenger_data_dict_instance.test_int_field, self.__passenger_data_dict["test_int_field"])
        self.assertEqual(
            passenger_data_dict_instance.test_kwarg_default_field,
            self.__passenger_data_dict["test_kwarg_default_field"],
        )
        self.assertEqual(
            passenger_data_dict_instance.test_kwarg_default_factory_field,
            self.__passenger_data_dict["test_kwarg_default_factory_field"],
        )
        self.assertEqual(passenger_data_dict_instance.passenger_id, self.__passenger_data_dict["passenger_id"])
        self.assertEqual(
            passenger_data_dict_instance.root_passenger_id, self.__passenger_data_dict["root_passenger_id"]
        )
