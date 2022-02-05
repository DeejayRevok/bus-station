from unittest import TestCase
from unittest.mock import Mock, patch

from rpyc import ThreadedServer

from bus_station.shared_terminal.rpyc_server import RPyCServer
from bus_station.shared_terminal.rpyc_service import RPyCService


class TestRPyCServer(TestCase):
    def setUp(self) -> None:
        self.rpyc_service_mock = Mock(spec=RPyCService)
        self.test_host = "test_host"
        self.test_port = 1234
        self.rpyc_server = RPyCServer(rpyc_service=self.rpyc_service_mock, host=self.test_host, port=self.test_port)

    @patch("bus_station.shared_terminal.rpyc_server.ThreadedServer")
    def test_run(self, threaded_sever_builder_mock):
        test_threaded_server_mock = Mock(spec=ThreadedServer)
        threaded_sever_builder_mock.return_value = test_threaded_server_mock

        self.rpyc_server.run()

        threaded_sever_builder_mock.assert_called_once_with(
            self.rpyc_service_mock, hostname=self.test_host, port=self.test_port
        )
        test_threaded_server_mock.start.assert_called_once_with()
        test_threaded_server_mock.close.assert_called_once_with()
