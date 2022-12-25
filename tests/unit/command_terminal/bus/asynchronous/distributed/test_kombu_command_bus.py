from unittest import TestCase
from unittest.mock import Mock, patch

from kombu import Connection, Producer
from kombu.transport.virtual import Channel

from bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus import KombuCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class TestKombuCommandBus(TestCase):
    @patch("bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus.Producer")
    def setUp(self, producer_builder_mock) -> None:
        self.producer_mock = Mock(spec=Producer)
        producer_builder_mock.return_value = self.producer_mock
        self.connection_mock = Mock(spec=Connection)
        self.channel_mock = Mock(spec=Channel)
        self.connection_mock.channel.return_value = self.channel_mock
        self.command_serializer_mock = Mock(spec=PassengerSerializer)
        self.command_registry_mock = Mock(spec=RemoteCommandRegistry)
        self.kombu_command_bus = KombuCommandBus(
            self.connection_mock,
            self.command_serializer_mock,
            self.command_registry_mock,
        )

    def test_transport_not_registered(self):
        test_command = Mock(spec=Command)
        self.command_registry_mock.get_command_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            self.kombu_command_bus.transport(test_command)

        self.assertEqual(test_command.passenger_name(), hnffc.exception.command_name)
        self.command_serializer_mock.serialize.assert_not_called()
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with(test_command.__class__)

    def test_transport_success(self):
        test_command = Mock(spec=Command)
        test_command_serialized = "test_command_serialized"
        self.command_serializer_mock.serialize.return_value = test_command_serialized
        self.command_registry_mock.get_commands_registered.return_value = [test_command.__class__]
        self.command_registry_mock.get_command_destination_contact.return_value = test_command.passenger_name()

        self.kombu_command_bus.transport(test_command)

        self.command_serializer_mock.serialize.assert_called_once_with(test_command)
        self.producer_mock.publish.assert_called_once_with(
            test_command_serialized,
            exchange="",
            routing_key=test_command.passenger_name(),
            retry=True,
            retry_policy={
                "interval_start": 0,
                "interval_step": 2,
                "interval_max": 10,
                "max_retries": 10,
            },
        )
