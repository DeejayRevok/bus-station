from unittest import TestCase
from unittest.mock import Mock, call, patch

from kombu import Connection, Exchange, Queue
from kombu.transport.virtual import Channel

from bus_station.event_terminal.bus_engine.kombu_event_bus_engine import KombuEventBusEngine
from bus_station.event_terminal.contact_not_found_for_event import ContactNotFoundForEvent
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.event_registry import EventRegistry
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer


class TestKombuEventBusEngine(TestCase):
    def setUp(self) -> None:
        self.broker_connection_mock = Mock(spec=Connection)
        self.channel_mock = Mock(spec=Channel)
        self.broker_connection_mock.channel.return_value = self.channel_mock
        self.event_registry_mock = Mock(spec=EventRegistry)
        self.event_receiver_mock = Mock(spec=PassengerReceiver)
        self.event_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.event_type_mock = Mock(spec=Event)
        self.event_consumer_mock = Mock(spec=EventConsumer)

    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Queue")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Exchange")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.PassengerKombuConsumer")
    def test_init_contact_not_found(self, consumer_builder_mock, exchange_builder_mock, queue_builder_mock):
        self.event_registry_mock.get_event_destination_contact.return_value = None

        with self.assertRaises(ContactNotFoundForEvent) as cnffe:
            KombuEventBusEngine(
                self.broker_connection_mock,
                self.event_registry_mock,
                self.event_receiver_mock,
                self.event_deserializer_mock,
                self.event_type_mock.__class__,
                self.event_consumer_mock,
            )

        self.assertEqual(self.event_type_mock.__class__.__name__, cnffe.exception.event_name)
        self.event_registry_mock.get_event_destination_contact.assert_called_once_with(
            self.event_type_mock.__class__, self.event_consumer_mock
        )
        consumer_builder_mock.assert_not_called()
        exchange_builder_mock.assert_not_called()
        queue_builder_mock.assert_not_called()

    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Queue")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Exchange")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.PassengerKombuConsumer")
    def test_init_contact_found(self, consumer_builder_mock, exchange_builder_mock, queue_builder_mock):
        test_queue = Mock(spec=Queue)
        queue_builder_mock.return_value = test_queue
        test_exchange = Mock(spec=Exchange)
        exchange_builder_mock.return_value = test_exchange
        test_queue_name = "test_queue"
        self.event_registry_mock.get_event_destination_contact.return_value = test_queue_name

        KombuEventBusEngine(
            self.broker_connection_mock,
            self.event_registry_mock,
            self.event_receiver_mock,
            self.event_deserializer_mock,
            self.event_type_mock.__class__,
            self.event_consumer_mock,
        )

        test_exchange.declare.assert_has_calls([call(), call(channel=self.channel_mock)])
        queue_builder_mock.assert_called_once_with(
            name=self.event_consumer_mock.__class__.__name__,
            exchange=test_exchange,
            queue_arguments={"x-dead-letter-exchange": "failed_events"},
        )
        test_queue.declare.assert_called_once_with(channel=self.channel_mock)
        consumer_builder_mock.assert_called_once_with(
            self.broker_connection_mock,
            test_queue,
            self.event_consumer_mock,
            self.event_type_mock.__class__,
            self.event_receiver_mock,
            self.event_deserializer_mock,
        )

    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Queue")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Exchange")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.PassengerKombuConsumer")
    def test_start(self, consumer_builder_mock, *_):
        test_kombu_consumer = Mock(spec=PassengerKombuConsumer)
        consumer_builder_mock.return_value = test_kombu_consumer
        engine = KombuEventBusEngine(
            self.broker_connection_mock,
            self.event_registry_mock,
            self.event_receiver_mock,
            self.event_deserializer_mock,
            self.event_type_mock.__class__,
            self.event_consumer_mock,
        )

        engine.start()

        test_kombu_consumer.run.assert_called_once_with()

    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Queue")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Exchange")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.PassengerKombuConsumer")
    def test_stop(self, consumer_builder_mock, *_):
        test_kombu_consumer = Mock(spec=PassengerKombuConsumer)
        consumer_builder_mock.return_value = test_kombu_consumer
        engine = KombuEventBusEngine(
            self.broker_connection_mock,
            self.event_registry_mock,
            self.event_receiver_mock,
            self.event_deserializer_mock,
            self.event_type_mock.__class__,
            self.event_consumer_mock,
        )

        engine.stop()

        test_kombu_consumer.stop.assert_called_once_with()
