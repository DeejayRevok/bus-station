from multiprocessing.queues import Queue
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine import MemoryQueueEventBusEngine
from bus_station.event_terminal.contact_not_found_for_event import ContactNotFoundForEvent
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.event_registry import EventRegistry
from bus_station.passengers.memory_queue_passenger_worker import MemoryQueuePassengerWorker
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer


class TestMemoryQueueEventBusEngine(TestCase):
    def setUp(self) -> None:
        self.event_registry_mock = Mock(spec=EventRegistry)
        self.event_receiver_mock = Mock(spec=PassengerReceiver)
        self.event_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.event_type_mock = Mock(spec=Event)
        self.event_consumer_mock = Mock(spec=EventConsumer)

    @patch("bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine.MemoryQueuePassengerWorker")
    def test_init_contact_not_found(self, passenger_worker_builder):
        self.event_registry_mock.get_event_destination_contact.return_value = None

        with self.assertRaises(ContactNotFoundForEvent) as cnffe:
            MemoryQueueEventBusEngine(
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
        passenger_worker_builder.assert_not_called()

    @patch("bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine.MemoryQueuePassengerWorker")
    def test_init_contact_found(self, passenger_worker_builder):
        memory_queue_passenger_worker_mock = Mock(spec=MemoryQueuePassengerWorker)
        passenger_worker_builder.return_value = memory_queue_passenger_worker_mock
        test_queue = Mock(spec=Queue)
        self.event_registry_mock.get_event_destination_contact.return_value = test_queue

        MemoryQueueEventBusEngine(
            self.event_registry_mock,
            self.event_receiver_mock,
            self.event_deserializer_mock,
            self.event_type_mock.__class__,
            self.event_consumer_mock,
        )

        self.event_registry_mock.get_event_destination_contact.assert_called_once_with(
            self.event_type_mock.__class__, self.event_consumer_mock
        )
        passenger_worker_builder.assert_called_once_with(
            test_queue, self.event_consumer_mock, self.event_receiver_mock, self.event_deserializer_mock
        )

    @patch("bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine.MemoryQueuePassengerWorker")
    def test_start(self, passenger_worker_builder):
        memory_queue_passenger_worker_mock = Mock(spec=MemoryQueuePassengerWorker)
        passenger_worker_builder.return_value = memory_queue_passenger_worker_mock
        engine = MemoryQueueEventBusEngine(
            self.event_registry_mock,
            self.event_receiver_mock,
            self.event_deserializer_mock,
            self.event_type_mock.__class__,
            self.event_consumer_mock,
        )

        engine.start()

        memory_queue_passenger_worker_mock.work.assert_called_once_with()

    @patch("bus_station.event_terminal.bus_engine.memory_queue_event_bus_engine.MemoryQueuePassengerWorker")
    def test_stop(self, passenger_worker_builder):
        memory_queue_passenger_worker_mock = Mock(spec=MemoryQueuePassengerWorker)
        passenger_worker_builder.return_value = memory_queue_passenger_worker_mock
        engine = MemoryQueueEventBusEngine(
            self.event_registry_mock,
            self.event_receiver_mock,
            self.event_deserializer_mock,
            self.event_type_mock.__class__,
            self.event_consumer_mock,
        )

        engine.stop()

        memory_queue_passenger_worker_mock.stop.assert_called_once_with()
