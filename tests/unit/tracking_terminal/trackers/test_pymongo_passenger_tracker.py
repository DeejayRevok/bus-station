from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.passengers.passenger import Passenger
from bus_station.shared_terminal.bus_stop import BusStop
from bus_station.tracking_terminal.models.passenger_tracking import PassengerTracking
from bus_station.tracking_terminal.repositories.implementations.pymongo.pymongo_passenger_tracking_repository import (
    PyMongoPassengerTrackingRepository,
)
from bus_station.tracking_terminal.trackers.passenger_tracking_not_found import PassengerTrackingNotFound
from bus_station.tracking_terminal.trackers.pymongo_passenger_tracker import PyMongoPassengerTracker


class TestPyMongoPassengerTracker(TestCase):
    def setUp(self) -> None:
        self.test_passenger_tracking_cls = Mock()
        self.pymongo_passenger_tracking_repository_mock = Mock(spec=PyMongoPassengerTrackingRepository)
        self.pymongo_passenger_tracking_repository_mock.model = self.test_passenger_tracking_cls
        self.pymongo_passenger_tracker = PyMongoPassengerTracker(self.pymongo_passenger_tracking_repository_mock)

    @patch("bus_station.tracking_terminal.trackers.passenger_tracker.datetime")
    @patch("bus_station.tracking_terminal.trackers.passenger_tracker.asdict")
    def test_start_tracking_success(self, asdict_mock, datetime_mock):
        test_datetime = Mock(spec=datetime)
        datetime_mock.now.return_value = test_datetime
        test_dict = {"test": "test"}
        asdict_mock.return_value = test_dict
        test_passenger = Mock(spec=Passenger)
        test_bus_stop = Mock(spec=BusStop)
        test_passenger_tracking = Mock(spec=PassengerTracking)
        self.test_passenger_tracking_cls.return_value = test_passenger_tracking
        self.pymongo_passenger_tracking_repository_mock.model = self.test_passenger_tracking_cls

        self.pymongo_passenger_tracker.start_tracking(test_passenger, test_bus_stop)

        self.test_passenger_tracking_cls.assert_called_once_with(
            id=str(id(test_passenger)),
            name=test_passenger.__class__.__name__,
            executor_name=test_bus_stop.__class__.__name__,
            data=test_dict,
            execution_start=test_datetime,
            execution_end=None,
        )
        self.pymongo_passenger_tracking_repository_mock.save.assert_called_once_with(test_passenger_tracking)

    def test_end_tracking_not_found_error(self):
        test_passenger = Mock(spec=Passenger)
        self.pymongo_passenger_tracking_repository_mock.find_by_id.return_value = None

        with self.assertRaises(PassengerTrackingNotFound) as ptnf:
            self.pymongo_passenger_tracker.end_tracking(test_passenger)

            self.assertEqual(test_passenger.__class__.__name__, ptnf.passenger_name)
            self.assertEqual(str(id(test_passenger)), ptnf.passenger_id)
        self.pymongo_passenger_tracking_repository_mock.find_by_id.assert_called_once_with(str(id(test_passenger)))
        self.pymongo_passenger_tracking_repository_mock.save.assert_not_called()

    @patch("bus_station.tracking_terminal.trackers.passenger_tracker.datetime")
    def test_end_tracking_success(self, datetime_mock):
        test_passenger = Mock(spec=Passenger)
        test_datetime = Mock(spec=datetime)
        datetime_mock.now.return_value = test_datetime
        test_passenger_tracking = Mock(spec=PassengerTracking)
        self.pymongo_passenger_tracking_repository_mock.find_by_id.return_value = test_passenger_tracking

        self.pymongo_passenger_tracker.end_tracking(test_passenger, test="test")

        self.assertEqual(test_datetime, test_passenger_tracking.execution_end)
        self.assertEqual("test", test_passenger_tracking.test)
        self.pymongo_passenger_tracking_repository_mock.save.assert_called_once_with(test_passenger_tracking)
