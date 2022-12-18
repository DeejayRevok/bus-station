from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.query_terminal.middleware.implementations.tracking_query_middleware import TrackingQueryMiddleware
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.tracking_terminal.trackers.passenger_tracker import PassengerTracker


class TestTrackingQueryMiddleware(TestCase):
    def setUp(self) -> None:
        self.passenger_tracker_mock = Mock(spec=PassengerTracker)
        self.tracking_query_middleware = TrackingQueryMiddleware(self.passenger_tracker_mock)

    def test_before_handle(self):
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)

        self.tracking_query_middleware.before_handle(test_query, test_query_handler)

        self.passenger_tracker_mock.start_tracking.assert_called_once_with(test_query, test_query_handler)

    @patch("bus_station.query_terminal.middleware.implementations.tracking_query_middleware.asdict")
    def test_after_handle_without_exception(self, asdict_mock):
        test_query_response_dict = {"test": "test"}
        asdict_mock.return_value = test_query_response_dict
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)
        test_query_response = Mock(spec=QueryResponse)

        query_response = self.tracking_query_middleware.after_handle(
            test_query, test_query_handler, test_query_response
        )

        self.assertEqual(test_query_response, query_response)
        self.passenger_tracker_mock.end_tracking.assert_called_once_with(
            test_query, response_data=test_query_response_dict, success=True
        )

    @patch("bus_station.query_terminal.middleware.implementations.tracking_query_middleware.asdict")
    def test_after_handle_with_exception(self, asdict_mock):
        test_query_response_dict = {"test": "test"}
        asdict_mock.return_value = test_query_response_dict
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)
        test_query_response = Mock(spec=QueryResponse)

        query_response = self.tracking_query_middleware.after_handle(
            test_query, test_query_handler, test_query_response, handling_exception=Exception("Test exception")
        )

        self.assertEqual(test_query_response, query_response)
        self.passenger_tracker_mock.end_tracking.assert_called_once_with(
            test_query, response_data=test_query_response_dict, success=False
        )
