from multiprocessing.context import Process
from unittest import TestCase
from unittest.mock import Mock, call, patch

from kombu import Connection, Exchange, Producer, Queue
from kombu.transport.virtual import Channel

from bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus import KombuEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
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
        self.kombu_event_bus = KombuEventBus(
            self.connection_mock, self.event_serializer_mock, self.event_deserializer_mock
        )
        self.kombu_event_bus._middleware_executor = self.middleware_executor_mock

    @patch("bus_station.event_terminal.bus.event_bus.get_type_hints")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Process")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Queue")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Exchange")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.PassengerKombuConsumer")
    def test_register_success(self, consumer_mock, exchange_mock, queue_mock, process_mock, get_type_hints_mock):
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
        get_type_hints_mock.return_value = {"event": test_event.__class__}

        self.kombu_event_bus.register(test_event_consumer)

        exchange_mock.assert_called_once_with(test_event.__class__.__name__, type="fanout")
        queue_mock.assert_called_once_with(
            test_event_consumer.__class__.__name__,
            exchange=test_exchange,
            queue_arguments={"x-dead-letter-exchange": "failed_events"},
        )
        consumer_mock.assert_called_once_with(
            self.connection_mock,
            test_queue,
            test_event_consumer,
            test_event.__class__,
            self.middleware_executor_mock,
            self.event_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_consumer.run)

    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Producer")
    @patch("bus_station.event_terminal.bus.event_bus.get_type_hints")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Process")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Queue")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Exchange")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.PassengerKombuConsumer")
    def test_execute_success(
        self, consumer_mock, exchange_mock, queue_mock, process_mock, get_type_hints_mock, producer_mock
    ):
        test_producer = Mock(spec=Producer)
        producer_mock.return_value = test_producer
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
        get_type_hints_mock.return_value = {"event": test_event.__class__}
        test_command_serialized = "test_command_serialized"
        self.event_serializer_mock.serialize.return_value = test_command_serialized
        self.kombu_event_bus.register(test_event_consumer)
        self.kombu_event_bus.start()

        self.kombu_event_bus.publish(test_event)

        exchange_mock.assert_has_calls(
            [
                call(test_event.__class__.__name__, type="fanout"),
                call("failed_events", type="fanout", channel=self.channel_mock),
            ]
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
        self.event_serializer_mock.serialize.assert_called_once_with(test_event)
        test_producer.publish.assert_called_once_with(
            test_command_serialized,
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
    @patch("bus_station.event_terminal.bus.event_bus.get_type_hints")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Process")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Queue")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Exchange")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.PassengerKombuConsumer")
    def test_start(self, consumer_mock, exchange_mock, queue_mock, process_mock, get_type_hints_mock, producer_mock):
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
        get_type_hints_mock.return_value = {"event": test_event.__class__}
        test_command_serialized = "test_command_serialized"
        self.event_serializer_mock.serialize.return_value = test_command_serialized
        self.kombu_event_bus.register(test_event_consumer)

        self.kombu_event_bus.start()

        exchange_mock.assert_has_calls(
            [
                call(test_event.__class__.__name__, type="fanout"),
                call("failed_events", type="fanout", channel=self.channel_mock),
            ]
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

    @patch("bus_station.event_terminal.bus.event_bus.get_type_hints")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Process")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Queue")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.Exchange")
    @patch("bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus.PassengerKombuConsumer")
    def test_stop(self, consumer_mock, exchange_mock, queue_mock, process_mock, get_type_hints_mock):
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
        get_type_hints_mock.return_value = {"event": test_event.__class__}
        test_command_serialized = "test_command_serialized"
        self.event_serializer_mock.serialize.return_value = test_command_serialized
        self.kombu_event_bus.register(test_event_consumer)

        self.kombu_event_bus.stop()

        exchange_mock.assert_called_once_with(test_event.__class__.__name__, type="fanout")
        queue_mock.assert_called_once_with(
            test_event_consumer.__class__.__name__,
            exchange=test_exchange,
            queue_arguments={"x-dead-letter-exchange": "failed_events"},
        )
        consumer_mock.assert_called_once_with(
            self.connection_mock,
            test_queue,
            test_event_consumer,
            test_event.__class__,
            self.middleware_executor_mock,
            self.event_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_consumer.run)
        test_process.join.assert_called_once_with()
        test_consumer.stop.assert_called_once_with()
