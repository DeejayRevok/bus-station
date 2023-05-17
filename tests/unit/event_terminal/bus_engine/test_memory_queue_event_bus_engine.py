from multiprocessing.queues import Queue
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine import MemoryQueueEventBusEngine
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.event_consumer_not_found import EventConsumerNotFound
from bus_station.event_terminal.event_consumer_registry import EventConsumerRegistry
from bus_station.passengers.memory_queue_passenger_worker import MemoryQueuePassengerWorker
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer


class TestMemoryQueueEventBusEngine(TestCase):
    def setUp(self) -> None:
        self.event_consumer_registry_mock = Mock(spec=EventConsumerRegistry)
        self.event_receiver_mock = Mock(spec=PassengerReceiver)
        self.event_deserializer_mock = Mock(spec=PassengerDeserializer)

    @patch("bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine.MemoryQueuePassengerWorker")
    def test_init_event_consumer_not_found(self, passenger_worker_builder):
        self.event_consumer_registry_mock.get_bus_stop_by_name.return_value = None

        with self.assertRaises(EventConsumerNotFound) as context:
            MemoryQueueEventBusEngine(
                self.event_consumer_registry_mock,
                self.event_receiver_mock,
                self.event_deserializer_mock,
                "test_event_consumer",
            )

        self.assertEqual("test_event_consumer", context.exception.event_consumer_name)
        self.event_consumer_registry_mock.get_bus_stop_by_name.assert_called_once_with("test_event_consumer")
        passenger_worker_builder.assert_not_called()

    @patch("bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine.memory_queue_factory")
    @patch("bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine.MemoryQueuePassengerWorker")
    def test_init_consumer_found(self, passenger_worker_builder, memory_queue_factory_mock):
        memory_queue_passenger_worker_mock = Mock(spec=MemoryQueuePassengerWorker)
        passenger_worker_builder.return_value = memory_queue_passenger_worker_mock
        test_queue = Mock(spec=Queue)
        memory_queue_factory_mock.queue_with_id.return_value = test_queue
        event_consumer_mock = Mock(spec=EventConsumer, **{"bus_stop_name.return_value": "test_event_consumer"})
        self.event_consumer_registry_mock.get_bus_stop_by_name.return_value = event_consumer_mock

        MemoryQueueEventBusEngine(
            self.event_consumer_registry_mock,
            self.event_receiver_mock,
            self.event_deserializer_mock,
            "test_event_consumer",
        )

        self.event_consumer_registry_mock.get_bus_stop_by_name.assert_called_once_with("test_event_consumer")
        memory_queue_factory_mock.queue_with_id.assert_called_once_with("test_event_consumer")
        passenger_worker_builder.assert_called_once_with(
            test_queue, event_consumer_mock, self.event_receiver_mock, self.event_deserializer_mock
        )

    @patch("bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine.memory_queue_factory")
    @patch("bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine.MemoryQueuePassengerWorker")
    def test_start(self, passenger_worker_builder, _):
        memory_queue_passenger_worker_mock = Mock(spec=MemoryQueuePassengerWorker)
        passenger_worker_builder.return_value = memory_queue_passenger_worker_mock
        engine = MemoryQueueEventBusEngine(
            self.event_consumer_registry_mock,
            self.event_receiver_mock,
            self.event_deserializer_mock,
            "test_event_consumer",
        )

        engine.start()

        memory_queue_passenger_worker_mock.work.assert_called_once_with()

    @patch("bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine.memory_queue_factory")
    @patch("bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine.MemoryQueuePassengerWorker")
    def test_stop(self, passenger_worker_builder, _):
        memory_queue_passenger_worker_mock = Mock(spec=MemoryQueuePassengerWorker)
        passenger_worker_builder.return_value = memory_queue_passenger_worker_mock
        engine = MemoryQueueEventBusEngine(
            self.event_consumer_registry_mock,
            self.event_receiver_mock,
            self.event_deserializer_mock,
            "test_event_consumer",
        )

        engine.stop()

        memory_queue_passenger_worker_mock.stop.assert_called_once_with()
