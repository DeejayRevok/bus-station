from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from rpyc import Service, ThreadedServer

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.rpyc_command_server import RPyCCommandServer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer


class TestRPyCCommandServer(TestCase):
    def setUp(self) -> None:
        self.command_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.command_receiver_mock = Mock(spec=PassengerReceiver)
        self.host = "test_host"
        self.port = 678
        self.rpyc_command_server = RPyCCommandServer(
            self.host, self.port, self.command_deserializer_mock, self.command_receiver_mock
        )

    @patch("bus_station.shared_terminal.rpyc_server.partial")
    def test_register_success(self, partial_mock):
        test_handler = Mock(spec=CommandHandler)
        test_command = Mock(spec=Command)

        self.rpyc_command_server.register(test_command.__class__, test_handler)

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

        self.rpyc_command_server.run()

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
