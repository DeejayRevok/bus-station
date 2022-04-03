from dataclasses import dataclass
from logging import getLogger

from bus_station.query_terminal.middleware.implementations.timing_query_middleware import TimingQueryMiddleware
from bus_station.query_terminal.middleware.query_middleware_receiver import QueryMiddlewareReceiver
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class QueryTest(Query):
    test_value: str


class QueryTestHandler(QueryHandler):
    def __init__(self):
        self.call_count = 0

    def handle(self, query: QueryTest) -> QueryResponse:
        self.call_count += 1
        return QueryResponse(data=query.test_value)


class TestTimingQueryMiddleware(IntegrationTestCase):
    def setUp(self) -> None:
        self.logger = getLogger()
        self.query_middleware_receiver = QueryMiddlewareReceiver()
        self.query_middleware_receiver.add_middleware_definition(TimingQueryMiddleware, self.logger, lazy=True)

    def test_receive_with_middleware_logs_timing(self):
        test_query_value = "test_query_value"
        test_query = QueryTest(test_value=test_query_value)
        test_query_handler = QueryTestHandler()

        with self.assertLogs(level="INFO") as logs:
            query_response = self.query_middleware_receiver.receive(test_query, test_query_handler)

            self.assertIn(f"Query {test_query} handled by {test_query_handler.__class__.__name__} in", logs.output[0])
        self.assertEqual(1, test_query_handler.call_count)
        self.assertEqual(test_query_value, query_response.data)
