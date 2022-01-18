from typing import Type
from unittest import TestCase
from unittest.mock import Mock, call

from bus_station.query_terminal.middleware.query_middleware import QueryMiddleware
from bus_station.query_terminal.middleware.query_middleware_executor import QueryMiddlewareExecutor
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse


class TestCommandMiddlewareExecutor(TestCase):
    def setUp(self) -> None:
        self.query_middleware_executor = QueryMiddlewareExecutor()

    def test_execute_success(self):
        parent_mock = Mock()
        test_query_response = Mock(spec=QueryResponse)
        test_middleware1_class = Mock(spec=Type[QueryMiddleware])
        test_middleware2_class = Mock(spec=Type[QueryMiddleware])
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)
        test_query_handler.handle.return_value = test_query_response
        test_middleware1_class().after_handle.return_value = test_query_response
        test_middleware2_class().after_handle.return_value = test_query_response
        parent_mock.middleware1_class = test_middleware1_class
        parent_mock.middleware2_class = test_middleware2_class
        parent_mock.handler = test_query_handler

        self.query_middleware_executor.add_middleware_definition(test_middleware1_class)
        self.query_middleware_executor.add_middleware_definition(test_middleware2_class)
        query_response = self.query_middleware_executor.execute(test_query, test_query_handler)

        parent_mock.assert_has_calls(
            [
                call.middleware1_class().before_handle(test_query, test_query_handler),
                call.middleware2_class().before_handle(test_query, test_query_handler),
                call.handler.handle(test_query),
                call.middleware2_class().after_handle(test_query, test_query_handler, test_query_response),
                call.middleware1_class().after_handle(test_query, test_query_handler, test_query_response),
            ]
        )
        self.assertEqual(test_query_response, query_response)
