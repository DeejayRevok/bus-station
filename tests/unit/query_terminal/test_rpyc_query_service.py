from unittest import TestCase
from unittest.mock import Mock, MagicMock

from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.query_terminal.rpyc_query_service import RPyCQueryService
from bus_station.query_terminal.middleware.query_middleware_executor import QueryMiddlewareExecutor
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.serialization.query_response_serializer import QueryResponseSerializer


class TestRPyCQueryService(TestCase):
    def setUp(self) -> None:
        self.query_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.query_response_serializer_mock = Mock(spec=QueryResponseSerializer)
        self.query_middleware_executor_mock = Mock(spec=QueryMiddlewareExecutor)
        self.rpyc_query_service = RPyCQueryService(
            self.query_deserializer_mock, self.query_response_serializer_mock, self.query_middleware_executor_mock
        )

    def test_register_success(self):
        test_handler = Mock(spec=QueryHandler)
        test_query = Mock(spec=Query)

        self.rpyc_query_service.register(test_query.__class__, test_handler)

        expected_query_callable_name = f"exposed_{test_query.__class__.__name__}"
        self.assertTrue(hasattr(self.rpyc_query_service, expected_query_callable_name))
        rpyc_service_callable = getattr(self.rpyc_query_service, expected_query_callable_name)
        self.assertEqual((test_handler, test_query.__class__), rpyc_service_callable.args)

    def test_query_executor_success(self):
        test_serialized_query = "test_serialized_query"
        test_query = Mock(spec=Query)
        test_query_handler = Mock(spec=QueryHandler)
        test_query_response = Mock(spec=QueryResponse)
        test_serialized_query_response = "test_serialized_query_response"
        self.query_deserializer_mock.deserialize.return_value = test_query
        self.query_middleware_executor_mock.execute.return_value = test_query_response
        self.query_response_serializer_mock.serialize.return_value = test_serialized_query_response

        serialized_query_response = self.rpyc_query_service.passenger_executor(
            test_query_handler, test_query.__class__, test_serialized_query
        )

        self.assertEqual(serialized_query_response, test_serialized_query_response)
        self.query_deserializer_mock.deserialize.assert_called_once_with(
            test_serialized_query, passenger_cls=test_query.__class__
        )
        self.query_middleware_executor_mock.execute.assert_called_once_with(test_query, test_query_handler)
        self.query_response_serializer_mock.serialize.assert_called_once_with(test_query_response)

    def test_query_executor_not_query(self):
        test_not_query = MagicMock()
        test_query_handler = Mock(spec=QueryHandler)
        test_serialized_not_query = "test_serialized_not_query"
        self.query_deserializer_mock.deserialize.return_value = test_not_query

        with self.assertRaises(TypeError):
            self.rpyc_query_service.passenger_executor(
                test_query_handler, test_not_query.__class__, test_serialized_not_query
            )

        self.query_deserializer_mock.deserialize.assert_called_once_with(
            test_serialized_not_query, passenger_cls=test_not_query.__class__
        )
