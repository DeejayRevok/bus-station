from logging import Logger
from unittest import TestCase
from unittest.mock import Mock, call, patch

from bus_station.query_terminal.middleware.implementations.timing_query_middleware import TimingQueryMiddleware
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse


class TestTimingQueryMiddleware(TestCase):
    def setUp(self) -> None:
        self.logger_mock = Mock(spec=Logger)
        self.timing_query_middleware = TimingQueryMiddleware(self.logger_mock)

    @patch("bus_station.query_terminal.middleware.implementations.timing_query_middleware.time")
    def test_before_handle(self, time_mock):
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)

        self.timing_query_middleware.before_handle(test_query, test_query_handler)

        time_mock.time.assert_called_once_with()

    @patch("bus_station.query_terminal.middleware.implementations.timing_query_middleware.time")
    def test_after_handle_without_exception(self, time_mock):
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)
        test_query_response = Mock(spec=QueryResponse)
        time_mock.time.side_effect = [1, 2]

        self.timing_query_middleware.before_handle(test_query, test_query_handler)
        query_response = self.timing_query_middleware.after_handle(test_query, test_query_handler, test_query_response)

        time_mock.time.assert_has_calls([call(), call()])
        self.logger_mock.info.assert_called_once_with(
            f"Query {test_query} handled successfully by {test_query_handler.bus_stop_name()} in 1 seconds"
        )
        self.assertEqual(test_query_response, query_response)

    @patch("bus_station.query_terminal.middleware.implementations.timing_query_middleware.time")
    def test_after_handle_with_exception(self, time_mock):
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)
        test_query_response = Mock(spec=QueryResponse)
        time_mock.time.side_effect = [1, 2]

        self.timing_query_middleware.before_handle(test_query, test_query_handler)
        query_response = self.timing_query_middleware.after_handle(
            test_query, test_query_handler, test_query_response, handling_exception=Exception("Test exception")
        )

        time_mock.time.assert_has_calls([call(), call()])
        self.logger_mock.info.assert_called_once_with(
            f"Query {test_query} handled wrongly by {test_query_handler.bus_stop_name()} in 1 seconds"
        )
        self.assertEqual(test_query_response, query_response)
