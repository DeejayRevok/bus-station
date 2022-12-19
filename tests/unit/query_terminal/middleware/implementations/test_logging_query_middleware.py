from logging import Logger
from unittest import TestCase
from unittest.mock import Mock

from bus_station.query_terminal.middleware.implementations.logging_query_middleware import LoggingQueryMiddleware
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse


class TestLoggingQueryMiddleware(TestCase):
    def setUp(self) -> None:
        self.logger_mock = Mock(spec=Logger)
        self.logging_query_middleware = LoggingQueryMiddleware(self.logger_mock)

    def test_before_handle(self):
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)

        self.logging_query_middleware.before_handle(test_query, test_query_handler)

        self.logger_mock.info.assert_called_once_with(
            f"Starting handling query {test_query} with {test_query_handler.__class__.__name__}"
        )

    def test_after_handle_without_exception(self):
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)
        test_query_response = Mock(spec=QueryResponse)

        query_response = self.logging_query_middleware.after_handle(test_query, test_query_handler, test_query_response)

        self.logger_mock.info.assert_called_once_with(
            f"Finished handling query {test_query} "
            f"with {test_query_handler.__class__.__name__} "
            f"with response: {test_query_response}"
        )
        self.assertEqual(test_query_response, query_response)
        self.logger_mock.exception.assert_not_called()

    def test_after_handle_with_exception(self):
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)
        test_query_response = Mock(spec=QueryResponse)
        test_exception = Exception("Test exception")

        query_response = self.logging_query_middleware.after_handle(
            test_query, test_query_handler, test_query_response, handling_exception=test_exception
        )

        self.logger_mock.info.assert_called_once_with(
            f"Finished handling query {test_query} "
            f"with {test_query_handler.__class__.__name__} "
            f"with response: {test_query_response}"
        )
        self.assertEqual(test_query_response, query_response)
        self.logger_mock.exception.assert_called_once_with(
            test_exception, exc_info=(test_exception.__class__, test_exception, test_exception.__traceback__)
        )
