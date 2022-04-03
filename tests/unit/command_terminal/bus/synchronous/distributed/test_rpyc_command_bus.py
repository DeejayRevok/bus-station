from multiprocessing.context import Process
from typing import Callable
from unittest import TestCase
from unittest.mock import Mock, patch

from rpyc import Connection

from bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus import RPyCCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.command_terminal.rpyc_command_service import RPyCCommandService
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.rpyc_server import RPyCServer


class TestRPyCCommandBus(TestCase):
    @patch("bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus.RPyCCommandService")
    def setUp(self, rpyc_command_service_mock) -> None:
        self.rpyc_command_service_mock = Mock(spec=RPyCCommandService)
        rpyc_command_service_mock.return_value = self.rpyc_command_service_mock
        self.command_serializer_mock = Mock(spec=PassengerSerializer)
        self.command_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.command_registry_mock = Mock(spec=RemoteCommandRegistry)
        self.command_receiver_mock = Mock(spec=PassengerReceiver[Command, CommandHandler])
        self.test_host = "test_host"
        self.test_port = 1234
        self.rpyc_command_bus = RPyCCommandBus(
            self.test_host,
            self.test_port,
            self.command_serializer_mock,
            self.command_deserializer_mock,
            self.command_registry_mock,
            self.command_receiver_mock,
        )

    @patch("bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus.Process")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus.RPyCServer")
    def test_start(self, rpyc_server_mock, process_mock):
        test_rpyc_server = Mock(spec=RPyCServer)
        rpyc_server_mock.return_value = test_rpyc_server
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_command = Mock(spec=Command)
        self.command_registry_mock.get_commands_registered.return_value = [test_command.__class__]
        test_command_handler = Mock(spec=CommandHandler)
        self.command_registry_mock.get_command_destination.return_value = test_command_handler

        self.rpyc_command_bus.start()

        rpyc_server_mock.assert_called_once_with(
            rpyc_service=self.rpyc_command_service_mock,
            port=self.test_port,
        )
        process_mock.assert_called_once_with(target=test_rpyc_server.run)
        test_process.start.assert_called_once_with()
        self.rpyc_command_service_mock.register.assert_called_once_with(test_command.__class__, test_command_handler)

    @patch("bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus.signal")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus.os")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus.Process")
    @patch("bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus.RPyCServer")
    def test_stop(self, rpyc_server_mock, process_mock, os_mock, signal_mock):
        test_rpyc_server = Mock(spec=RPyCServer)
        rpyc_server_mock.return_value = test_rpyc_server
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        self.command_registry_mock.get_commands_registered.return_value = []
        self.rpyc_command_bus.start()

        self.rpyc_command_bus.stop()

        rpyc_server_mock.assert_called_once_with(
            rpyc_service=self.rpyc_command_service_mock,
            port=self.test_port,
        )
        process_mock.assert_called_once_with(target=test_rpyc_server.run)
        test_process.start.assert_called_once_with()
        os_mock.kill.assert_called_once_with(test_process.pid, signal_mock.SIGINT)
        test_process.join.assert_called_once_with()

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

        connect_mock.assert_called_once_with(test_host, port=test_port)
        self.command_serializer_mock.serialize.assert_called_once_with(test_command)
        test_rpyc_callable.assert_called_once_with(test_serialized_command)
        test_rpyc_connection.close.assert_called_once_with()
