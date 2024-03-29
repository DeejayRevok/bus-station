from dataclasses import dataclass
from logging import getLogger

from bus_station.query_terminal.middleware.implementations.logging_query_middleware import LoggingQueryMiddleware
from bus_station.query_terminal.middleware.query_middleware_receiver import QueryMiddlewareReceiver
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class QueryTest(Query):
    test_value: str
    raise_exception: bool


class QueryTestHandler(QueryHandler):
    def __init__(self):
        self.call_count = 0

    def handle(self, query: QueryTest) -> QueryResponse:
        self.call_count += 1
        if query.raise_exception is True:
            raise Exception("Test exception")
        return QueryResponse(data=query.test_value)


class TestLoggingQueryMiddleware(IntegrationTestCase):
    def setUp(self) -> None:
        self.logger = getLogger()
        self.query_middleware_receiver = QueryMiddlewareReceiver()
        self.query_middleware_receiver.add_middleware_definition(LoggingQueryMiddleware, self.logger, lazy=False)

    def test_receive_with_middleware_logs_without_exception(self):
        test_query_value = "test_query_value"
        test_query = QueryTest(test_value=test_query_value, raise_exception=False)
        test_query_handler = QueryTestHandler()

        with self.assertLogs(level="INFO") as logs:
            query_response = self.query_middleware_receiver.receive(test_query, test_query_handler)

            self.assertIn(
                f"Starting handling query {test_query} with {test_query_handler.bus_stop_name()}", logs.output[0]
            )
            self.assertIn(
                f"Finished handling query {test_query} with {test_query_handler.bus_stop_name()}", logs.output[1]
            )
        self.assertEqual(1, test_query_handler.call_count)
        self.assertEqual(test_query_value, query_response.data)

    def test_receive_with_middleware_logs_with_exception(self):
        test_query = QueryTest(test_value="test", raise_exception=True)
        test_query_handler = QueryTestHandler()

        with self.assertLogs(level="ERROR") as logs:
            with self.assertRaises(Exception) as exception_context:
                self.query_middleware_receiver.receive(test_query, test_query_handler)

            self.assertEqual("Test exception", str(exception_context.exception))
            self.assertIn("Test exception", logs.output[0])
            self.assertIn("Traceback", logs.output[0])
        self.assertEqual(1, test_query_handler.call_count)
