from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from rpyc import Service, ThreadedServer

from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.query_terminal.query import Query
from bus_station.query_terminal.query_handler import QueryHandler
from bus_station.query_terminal.rpyc_query_server import RPyCQueryServer
from bus_station.query_terminal.serialization.query_response_serializer import QueryResponseSerializer


class TestRPyCQueryServer(TestCase):
    def setUp(self) -> None:
        self.query_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.query_response_serializer_mock = Mock(spec=QueryResponseSerializer)
        self.query_receiver_mock = Mock(spec=PassengerReceiver)
        self.host = "test_host"
        self.port = 12341
        self.rpyc_query_server = RPyCQueryServer(
            self.host,
            self.port,
            self.query_deserializer_mock,
            self.query_receiver_mock,
            self.query_response_serializer_mock,
        )

    @patch("bus_station.shared_terminal.rpyc_server.partial")
    def test_register(self, partial_mock):
        test_handler = Mock(spec=QueryHandler)
        test_query = Mock(spec=Query)

        self.rpyc_query_server.register(test_query.__class__, test_handler)

        partial_mock.assert_called_once()

    @patch("bus_station.shared_terminal.rpyc_server.type")
    @patch("bus_station.shared_terminal.rpyc_server.ThreadedServer")
    def test_run(self, threaded_sever_builder_mock, type_mock):
        service_class_mock = MagicMock()
        type_mock.return_value = service_class_mock
        service_instance_mock = Mock(spec=Service)
        service_class_mock.return_value = service_instance_mock
        test_threaded_server_mock = Mock(spec=ThreadedServer)
        threaded_sever_builder_mock.return_value = test_threaded_server_mock

        self.rpyc_query_server.run()

        threaded_sever_builder_mock.assert_called_once_with(
            service=service_instance_mock,
            hostname=self.host,
            port=self.port,
            protocol_config={"allow_public_attrs": True},
        )
        test_threaded_server_mock.start.assert_called_once_with()
        test_threaded_server_mock.close.assert_called_once_with()
        service_class_mock.assert_called_once_with()
        type_mock.assert_called_once_with("RPyCServiceClass", (Service,), {})
