from unittest import TestCase
from unittest.mock import Mock, patch

from kombu import Connection, Producer
from kombu.transport.virtual import Channel

from bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus import KombuCommandBus
from bus_station.command_terminal.command import Command
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
        self.kombu_command_bus = KombuCommandBus(
            self.connection_mock,
            self.command_serializer_mock,
        )

    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    def test_transport_success(self, get_context_root_passenger_id_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        test_command_serialized = "test_command_serialized"
        self.command_serializer_mock.serialize.return_value = test_command_serialized

        self.kombu_command_bus.transport(test_command)

        self.command_serializer_mock.serialize.assert_called_once_with(test_command)
        self.producer_mock.publish.assert_called_once_with(
            test_command_serialized,
            exchange="",
            routing_key="test_command",
            retry=True,
            retry_policy={
                "interval_start": 0,
                "interval_step": 2,
                "interval_max": 10,
                "max_retries": 10,
            },
        )
        test_command.set_root_passenger_id.assert_called_once_with("test_root_passenger_id")
