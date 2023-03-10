from unittest import TestCase

from bus_station.command_terminal.command import Command
from bus_station.event_terminal.event import Event
from bus_station.passengers.passenger import Passenger
from bus_station.query_terminal.query import Query
from bus_station.tracking_terminal.models.command_tracking import CommandTracking
from bus_station.tracking_terminal.models.event_tracking import EventTracking
from bus_station.tracking_terminal.models.passenger_model_tracking_map import PassengerModelTrackingMap
from bus_station.tracking_terminal.models.query_tracking import QueryTracking


class TestCommand(Command):
    pass

class TestEvent(Event):
    pass

class TestQuery(Query):
    pass

class TestNotSupported(Passenger):
    @classmethod
    def passenger_name(cls) -> str:
        return "test"


class TestPassengerModelTrackingMap(TestCase):
    def setUp(self) -> None:
        self.passenger_model_tracking_map = PassengerModelTrackingMap()

    def test_get_tracking_model_passenger_supported(self):
        scenarios = [
            {
                "message": "Test map command",
                "passenger": TestCommand(),
                "expected_result": CommandTracking
            },
            {
                "message": "Test map event",
                "passenger": TestEvent(),
                "expected_result": EventTracking
            },
            {
                "message": "Test map query",
                "passenger": TestQuery(),
                "expected_result": QueryTracking
            }
        ]
        for scenario in scenarios:
            with self.subTest(scenario["message"]):
                result = self.passenger_model_tracking_map.get_tracking_model(scenario["passenger"])

                self.assertEqual(scenario["expected_result"], result)

    def test_get_tracking_model_not_supported(self):
        with self.assertRaises(NotImplementedError):
            self.passenger_model_tracking_map.get_tracking_model(TestNotSupported())
