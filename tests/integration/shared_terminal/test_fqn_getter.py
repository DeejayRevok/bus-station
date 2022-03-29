from unittest import TestCase

from bus_station.shared_terminal.fqn_getter import FQNGetter


class TestFQNGetter(TestCase):
    def setUp(self) -> None:
        self.fqn_getter = FQNGetter()

    def test_get_from_instance_success(self):
        fqn = self.fqn_getter.get(self.fqn_getter)

        expected_fqn = "bus_station.shared_terminal.fqn_getter.FQNGetter"
        self.assertEqual(expected_fqn, fqn)

    def test_get_from_class_success(self):
        fqn = self.fqn_getter.get(FQNGetter)

        expected_fqn = "bus_station.shared_terminal.fqn_getter.FQNGetter"
        self.assertEqual(expected_fqn, fqn)
