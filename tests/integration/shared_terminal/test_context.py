from contextvars import copy_context
from unittest import TestCase

from bus_station.shared_terminal.context import get_context_root_passenger_id, set_context_root_passenger_id


class TestDistributed(TestCase):
    def setUp(self) -> None:
        set_context_root_passenger_id(None)

    def test_set_context_root_passenger_id(self):
        set_context_root_passenger_id("test_root_passenger_id")

        context = copy_context()
        context_vars = list(context.items())
        self.assertEqual("bus_station_root_passenger_id", context_vars[0][0].name)
        self.assertEqual("test_root_passenger_id", context_vars[0][1])

    def test_get_context_root_passenger_id(self):
        set_context_root_passenger_id("test_root_passenger_id")

        context_root_passenger_id = get_context_root_passenger_id()

        self.assertEqual("test_root_passenger_id", context_root_passenger_id)
