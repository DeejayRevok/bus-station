from unittest import TestCase
from unittest.mock import Mock, patch

from kombu import Connection

from bus_station.shared_terminal.broker_connection.connection_parameters.connection_parameters import (
    ConnectionParameters,
)
from bus_station.shared_terminal.factories.kombu_connection_factory import KombuConnectionFactory


@patch("bus_station.shared_terminal.factories.kombu_connection_factory.Connection")
class TestBrokerConnectionFactory(TestCase):
    def setUp(self) -> None:
        self.kombu_connection_factory = KombuConnectionFactory()

    def test_get_connection(self, kombu_connection_mock):
        test_connection_string = "test_connection_string"
        test_connection_parameters = Mock(spec=ConnectionParameters)
        test_connection_parameters.get_connection_string.return_value = test_connection_string
        test_connection = Mock(spec=Connection)
        kombu_connection_mock.return_value = test_connection

        created_connection = self.kombu_connection_factory.get_connection(test_connection_parameters)

        self.assertEqual(test_connection, created_connection)
        test_connection_parameters.get_connection_string.assert_called_once_with()
        kombu_connection_mock.assert_called_once_with(test_connection_string)
