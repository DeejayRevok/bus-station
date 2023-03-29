from unittest import TestCase
from unittest.mock import Mock, patch

from kombu import Connection, Producer
from kombu.transport.virtual import Channel

from bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus import KombuEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.registry.remote_event_registry import RemoteEventRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class TestKombuEventBus(TestCase):
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Producer")
    def setUp(self, producer_builder_mock) -> None:
        self.producer_mock = Mock(spec=Producer)
        producer_builder_mock.return_value = self.producer_mock
        self.connection_mock = Mock(spec=Connection)
        self.channel_mock = Mock(spec=Channel)
        self.connection_mock.channel.return_value = self.channel_mock
        self.event_serializer_mock = Mock(spec=PassengerSerializer)
        self.event_registry_mock = Mock(spec=RemoteEventRegistry)
        self.kombu_event_bus = KombuEventBus(
            self.connection_mock,
            self.event_serializer_mock,
            self.event_registry_mock,
        )

    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    def test_transport_sucess(self, get_context_root_passenger_id_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id"
        test_event = Mock(spec=Event, **{"passenger_name.return_value": "test_event"})
        test_event_serialized = "test_event_serialized"
        self.event_serializer_mock.serialize.return_value = test_event_serialized
        self.event_registry_mock.get_event_destination_contacts.return_value = ["test_event"]

        self.kombu_event_bus.transport(test_event)

        self.event_serializer_mock.serialize.assert_called_once_with(test_event)
        self.producer_mock.publish.assert_called_once_with(
            test_event_serialized,
            exchange="test_event",
            retry=True,
            retry_policy={
                "interval_start": 0,
                "interval_step": 2,
                "interval_max": 10,
                "max_retries": 10,
            },
        )
        test_event.set_root_passenger_id.assert_called_once_with("test_root_passenger_id")
