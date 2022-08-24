from typing import Callable
from unittest import TestCase
from unittest.mock import Mock, patch

from rpyc import Connection

from bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus import RPyCCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class TestRPyCCommandBus(TestCase):
    def setUp(self) -> None:
        self.command_serializer_mock = Mock(spec=PassengerSerializer)
        self.command_registry_mock = Mock(spec=RemoteCommandRegistry)
        self.rpyc_command_bus = RPyCCommandBus(
            self.command_serializer_mock,
            self.command_registry_mock,
        )

    def test_transport_not_registered(self):
        test_command = Mock(spec=Command, name="TestCommand")
        self.command_registry_mock.get_command_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            self.rpyc_command_bus.transport(test_command)

        self.assertEqual(test_command.__class__.__name__, hnffc.exception.command_name)
        self.command_serializer_mock.serialize.assert_not_called()
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with(test_command.__class__)

    @patch("bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus.connect")
    def test_transport_success(self, connect_mock):
        test_command = Mock(spec=Command, name="TestCommand")
        test_host = "test_host"
        test_port = "41124"
        self.command_registry_mock.get_command_destination_contact.return_value = f"{test_host}:{test_port}"
        test_rpyc_connection = Mock(spec=Connection)
        connect_mock.return_value = test_rpyc_connection
        test_serialized_command = "test_serialized_command"
        self.command_serializer_mock.serialize.return_value = test_serialized_command
        test_rpyc_callable = Mock(spec=Callable)
        setattr(test_rpyc_connection.root, test_command.__class__.__name__, test_rpyc_callable)

        self.rpyc_command_bus.transport(test_command)

        connect_mock.assert_called_once_with(test_host, port=test_port, config={"allow_public_attrs": True})
        self.command_serializer_mock.serialize.assert_called_once_with(test_command)
        test_rpyc_callable.assert_called_once_with(test_serialized_command)
        test_rpyc_connection.close.assert_called_once_with()
