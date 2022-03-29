from multiprocessing.context import Process
from typing import Callable
from unittest import TestCase
from unittest.mock import Mock, patch

from rpyc import Connection

from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.query_terminal.bus.synchronous.distributed.rpyc_query_bus import RPyCQueryBus
from bus_station.query_terminal.handler_not_found_for_query import HandlerNotFoundForQuery
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.registry.remote_query_registry import RemoteQueryRegistry
from bus_station.query_terminal.rpyc_query_service import RPyCQueryService
from bus_station.query_terminal.serialization.query_response_deserializer import QueryResponseDeserializer
from bus_station.query_terminal.serialization.query_response_serializer import QueryResponseSerializer
from bus_station.shared_terminal.rpyc_server import RPyCServer


class TestRPyCQueryBus(TestCase):
    @patch("bus_station.query_terminal.bus.synchronous.distributed.rpyc_query_bus.RPyCQueryService")
    def setUp(self, rpyc_query_service_mock) -> None:
        self.rpyc_query_service_mock = Mock(spec=RPyCQueryService)
        rpyc_query_service_mock.return_value = self.rpyc_query_service_mock
        self.query_serializer_mock = Mock(spec=PassengerSerializer)
        self.query_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.query_response_serializer_mock = Mock(spec=QueryResponseSerializer)
        self.query_response_deserializer_mock = Mock(spec=QueryResponseDeserializer)
        self.query_registry_mock = Mock(spec=RemoteQueryRegistry)
        self.test_host = "test_host"
        self.test_port = 1234
        self.rpyc_query_bus = RPyCQueryBus(
            self.test_host,
            self.test_port,
            self.query_serializer_mock,
            self.query_deserializer_mock,
            self.query_response_serializer_mock,
            self.query_response_deserializer_mock,
            self.query_registry_mock,
        )

    @patch("bus_station.query_terminal.bus.synchronous.distributed.rpyc_query_bus.Process")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.rpyc_query_bus.RPyCServer")
    def test_start(self, rpyc_server_mock, process_mock):
        test_rpyc_server = Mock(spec=RPyCServer)
        rpyc_server_mock.return_value = test_rpyc_server
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_query = Mock(spec=Query)
        self.query_registry_mock.get_queries_registered.return_value = [test_query.__class__]
        test_query_handler = Mock(spec=QueryHandler)
        self.query_registry_mock.get_query_destination.return_value = test_query_handler

        self.rpyc_query_bus.start()

        rpyc_server_mock.assert_called_once_with(
            rpyc_service=self.rpyc_query_service_mock,
            port=self.test_port,
        )
        process_mock.assert_called_once_with(target=test_rpyc_server.run)
        test_process.start.assert_called_once_with()
        self.rpyc_query_service_mock.register.assert_called_once_with(test_query.__class__, test_query_handler)

    @patch("bus_station.query_terminal.bus.synchronous.distributed.rpyc_query_bus.signal")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.rpyc_query_bus.os")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.rpyc_query_bus.Process")
    @patch("bus_station.query_terminal.bus.synchronous.distributed.rpyc_query_bus.RPyCServer")
    def test_stop(self, rpyc_server_mock, process_mock, os_mock, signal_mock):
        test_rpyc_server = Mock(spec=RPyCServer)
        rpyc_server_mock.return_value = test_rpyc_server
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_query = Mock(spec=Query)
        self.query_registry_mock.get_queries_registered.return_value = [test_query.__class__]
        self.rpyc_query_bus.start()

        self.rpyc_query_bus.stop()

        rpyc_server_mock.assert_called_once_with(
            rpyc_service=self.rpyc_query_service_mock,
            port=self.test_port,
        )
        process_mock.assert_called_once_with(target=test_rpyc_server.run)
        test_process.start.assert_called_once_with()
        os_mock.kill.assert_called_once_with(test_process.pid, signal_mock.SIGINT)
        test_process.join.assert_called_once_with()

    def test_execute_not_registered(self):
        test_query = Mock(spec=Query, name="TestQuery")
        self.query_registry_mock.get_query_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForQuery) as hnffq:
            self.rpyc_query_bus.execute(test_query)

        self.assertEqual(test_query.__class__.__name__, hnffq.exception.query_name)
        self.query_serializer_mock.serialize.assert_not_called()
        self.query_registry_mock.get_query_destination_contact.assert_called_once_with(test_query.__class__)

    @patch("bus_station.query_terminal.bus.synchronous.distributed.rpyc_query_bus.connect")
    def test_execute_success(self, connect_mock):
        test_query = Mock(spec=Query, name="TestQuery")
        test_host = "test_host"
        test_port = "41124"
        self.query_registry_mock.get_query_destination_contact.return_value = f"{test_host}:{test_port}"
        test_rpyc_connection = Mock(spec=Connection)
        connect_mock.return_value = test_rpyc_connection
        test_serialized_query = "test_serialized_query"
        self.query_serializer_mock.serialize.return_value = test_serialized_query
        test_rpyc_callable = Mock(spec=Callable)
        setattr(test_rpyc_connection.root, test_query.__class__.__name__, test_rpyc_callable)
        test_query_response = Mock(spec=QueryResponse)
        test_serialized_query_response = "test_serialized_query_response"
        test_rpyc_callable.return_value = test_serialized_query_response
        self.query_response_deserializer_mock.deserialize.return_value = test_query_response

        query_response = self.rpyc_query_bus.execute(test_query)

        self.assertEqual(test_query_response, query_response)
        connect_mock.assert_called_once_with(test_host, port=test_port)
        self.query_serializer_mock.serialize.assert_called_once_with(test_query)
        test_rpyc_callable.assert_called_once_with(test_serialized_query)
        self.query_response_deserializer_mock.deserialize.assert_called_once_with(test_serialized_query_response)
        test_rpyc_connection.close.assert_called_once_with()
