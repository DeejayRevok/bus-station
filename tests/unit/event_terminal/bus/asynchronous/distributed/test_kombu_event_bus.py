from multiprocessing.context import Process
from unittest import TestCase
from unittest.mock import Mock, call, patch

from kombu import Connection, Exchange, Producer, Queue
from kombu.transport.virtual import Channel

from bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus import KombuEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.event_registry import EventRegistry
from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor
from bus_station.passengers.passenger_kombu_consumer import PassengerKombuConsumer
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class TestKombuEventBus(TestCase):
    def setUp(self) -> None:
        self.connection_mock = Mock(spec=Connection)
        self.channel_mock = Mock(spec=Channel)
        self.connection_mock.channel.return_value = self.channel_mock
        self.event_serializer_mock = Mock(spec=PassengerSerializer)
        self.event_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.middleware_executor_mock = Mock(spec=PassengerMiddlewareExecutor)
        self.event_registry_mock = Mock(spec=EventRegistry)
        self.kombu_event_bus = KombuEventBus(
            self.connection_mock, self.event_serializer_mock, self.event_deserializer_mock, self.event_registry_mock
        )
        self.kombu_event_bus._middleware_executor = self.middleware_executor_mock

    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Producer")
    def test_execute_success(self, producer_mock):
        test_producer = Mock(spec=Producer)
        producer_mock.return_value = test_producer
        test_event = Mock(spec=Event)
        test_event_serialized = "test_command_serialized"
        self.event_serializer_mock.serialize.return_value = test_event_serialized
        self.event_registry_mock.get_events_registered.return_value = []
        self.event_registry_mock.get_event_destination_contacts.return_value = [test_event.__class__.__name__]
        self.kombu_event_bus.start()

        self.kombu_event_bus.publish(test_event)

        self.event_serializer_mock.serialize.assert_called_once_with(test_event)
        test_producer.publish.assert_called_once_with(
            test_event_serialized,
            exchange=test_event.__class__.__name__,
            retry=True,
            retry_policy={
                "interval_start": 0,
                "interval_step": 2,
                "interval_max": 10,
                "max_retries": 10,
            },
        )

    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Producer")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Process")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Queue")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Exchange")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.PassengerKombuConsumer")
    def test_start(self, consumer_mock, exchange_mock, queue_mock, process_mock, producer_mock):
        test_queue = Mock(spec=Queue)
        queue_mock.return_value = test_queue
        test_exchange = Mock(spec=Exchange)
        exchange_mock.return_value = test_exchange
        test_consumer = Mock(spec=PassengerKombuConsumer)
        consumer_mock.return_value = test_consumer
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_event_consumer = Mock(spec=EventConsumer)
        test_event = Mock(spec=Event)
        self.event_registry_mock.get_events_registered.return_value = [test_event.__class__]
        self.event_registry_mock.get_event_destination_contacts.return_value = [test_event.__class__.__name__]
        self.event_registry_mock.get_event_destinations.return_value = [test_event_consumer]

        self.kombu_event_bus.start()

        self.assertCountEqual(
            [
                call("failed_events", type="fanout", channel=self.channel_mock),
                call(test_event.__class__.__name__, type="fanout"),
            ],
            exchange_mock.call_args_list,
        )
        test_exchange.declare.assert_has_calls([call(), call(channel=self.channel_mock)])
        queue_mock.assert_called_once_with(
            test_event_consumer.__class__.__name__,
            exchange=test_exchange,
            queue_arguments={"x-dead-letter-exchange": "failed_events"},
        )
        test_queue.declare.assert_called_once_with(channel=self.channel_mock)
        consumer_mock.assert_called_once_with(
            self.connection_mock,
            test_queue,
            test_event_consumer,
            test_event.__class__,
            self.middleware_executor_mock,
            self.event_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_consumer.run)
        test_process.start.assert_called_once_with()
        producer_mock.assert_called_once_with(self.channel_mock)

    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Producer")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Process")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Queue")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Exchange")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.PassengerKombuConsumer")
    def test_stop(self, consumer_mock, exchange_mock, queue_mock, process_mock, producer_mock):
        test_queue = Mock(spec=Queue)
        queue_mock.return_value = test_queue
        test_exchange = Mock(spec=Exchange)
        exchange_mock.return_value = test_exchange
        test_consumer = Mock(spec=PassengerKombuConsumer)
        consumer_mock.return_value = test_consumer
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_event_consumer = Mock(spec=EventConsumer)
        test_event = Mock(spec=Event)
        test_producer = Mock(spec=Producer)
        producer_mock.return_value = test_producer
        self.event_registry_mock.get_events_registered.return_value = [test_event.__class__]
        self.event_registry_mock.get_event_destination_contacts.return_value = [test_event.__class__.__name__]
        self.event_registry_mock.get_event_destinations.return_value = [test_event_consumer]
        self.kombu_event_bus.start()

        self.kombu_event_bus.stop()

        test_process.join.assert_called_once_with()
        test_consumer.stop.assert_called_once_with()
        test_producer.release.assert_called_once_with()
        self.connection_mock.release.assert_called_once_with()
