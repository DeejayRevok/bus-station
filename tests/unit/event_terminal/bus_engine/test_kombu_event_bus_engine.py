from unittest import TestCase
from unittest.mock import Mock, call, patch

from kombu import Connection, Exchange, Queue
from kombu.transport.virtual import Channel

from bus_station.event_terminal.bus_engine.kombu_event_bus_engine import KombuEventBusEngine
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.event_consumer_not_found import EventConsumerNotFound
from bus_station.event_terminal.event_consumer_registry import EventConsumerRegistry
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer


class TestKombuEventBusEngine(TestCase):
    def setUp(self) -> None:
        self.broker_connection_mock = Mock(spec=Connection)
        self.channel_mock = Mock(spec=Channel)
        self.broker_connection_mock.channel.return_value = self.channel_mock
        self.event_consumer_registry_mock = Mock(spec=EventConsumerRegistry)
        self.event_receiver_mock = Mock(spec=PassengerReceiver)
        self.event_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.event_consumer_mock = Mock(spec=EventConsumer)
        self.event_type_mock = Mock(spec=Event)

    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Queue")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Exchange")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.PassengerKombuConsumer")
    def test_init_event_consumer_not_found(self, consumer_builder_mock, exchange_builder_mock, queue_builder_mock):
        self.event_consumer_registry_mock.get_bus_stop_by_name.return_value = None

        with self.assertRaises(EventConsumerNotFound) as context:
            KombuEventBusEngine(
                self.broker_connection_mock,
                self.event_receiver_mock,
                self.event_consumer_registry_mock,
                self.event_deserializer_mock,
                "test_event_consumer",
            )

        self.assertEqual("test_event_consumer", context.exception.event_consumer_name)
        self.event_consumer_registry_mock.get_bus_stop_by_name.assert_called_once_with("test_event_consumer")
        consumer_builder_mock.assert_not_called()
        exchange_builder_mock.assert_not_called()
        queue_builder_mock.assert_not_called()

    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.resolve_passenger_class_from_bus_stop")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Queue")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Exchange")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.PassengerKombuConsumer")
    def test_init_contact_found(
        self, consumer_builder_mock, exchange_builder_mock, queue_builder_mock, passenger_resolver_mock
    ):
        test_queue = Mock(spec=Queue)
        queue_builder_mock.return_value = test_queue
        test_exchange = Mock(spec=Exchange)
        exchange_builder_mock.return_value = test_exchange
        self.event_consumer_registry_mock.get_bus_stop_by_name.return_value = self.event_consumer_mock
        test_event = Mock(spec=Event)
        passenger_resolver_mock.return_value = test_event

        KombuEventBusEngine(
            self.broker_connection_mock,
            self.event_receiver_mock,
            self.event_consumer_registry_mock,
            self.event_deserializer_mock,
            "test_event_consumer",
        )

        test_exchange.declare.assert_has_calls([call(), call(channel=self.channel_mock)])
        queue_builder_mock.assert_called_once_with(
            name=self.event_consumer_mock.bus_stop_name(),
            exchange=test_exchange,
            queue_arguments={"x-dead-letter-exchange": "failed_events"},
        )
        test_queue.declare.assert_called_once_with(channel=self.channel_mock)
        consumer_builder_mock.assert_called_once_with(
            self.broker_connection_mock,
            test_queue,
            self.event_consumer_mock,
            test_event,
            self.event_receiver_mock,
            self.event_deserializer_mock,
        )

    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.resolve_passenger_class_from_bus_stop")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Queue")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Exchange")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.PassengerKombuConsumer")
    def test_start(self, consumer_builder_mock, *_):
        test_kombu_consumer = Mock(spec=PassengerKombuConsumer)
        consumer_builder_mock.return_value = test_kombu_consumer
        engine = KombuEventBusEngine(
            self.broker_connection_mock,
            self.event_receiver_mock,
            self.event_consumer_registry_mock,
            self.event_deserializer_mock,
            "test_event_consumer",
        )

        engine.start()

        test_kombu_consumer.run.assert_called_once_with()

    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.resolve_passenger_class_from_bus_stop")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Queue")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.Exchange")
    @patch("bus_station.event_terminal.bus_engine.kombu_event_bus_engine.PassengerKombuConsumer")
    def test_stop(self, consumer_builder_mock, *_):
        test_kombu_consumer = Mock(spec=PassengerKombuConsumer)
        consumer_builder_mock.return_value = test_kombu_consumer
        engine = KombuEventBusEngine(
            self.broker_connection_mock,
            self.event_receiver_mock,
            self.event_consumer_registry_mock,
            self.event_deserializer_mock,
            "test_event_consumer",
        )

        engine.stop()

        test_kombu_consumer.stop.assert_called_once_with()
