from multiprocessing.queues import Queue
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.event_terminal.bus.asynchronous.memory_queue_event_bus import MemoryQueueEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.event_consumer_registry import EventConsumerRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class TestMemoryQueueEventBus(TestCase):
    def setUp(self) -> None:
        self.event_serializer_mock = Mock(spec=PassengerSerializer)
        self.event_consumer_registry_mock = Mock(spec=EventConsumerRegistry)
        self.process_event_bus = MemoryQueueEventBus(
            self.event_serializer_mock,
            self.event_consumer_registry_mock,
        )

    @patch("bus_station.event_terminal.bus.asynchronous.memory_queue_event_bus.memory_queue_factory")
    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    def test_transport_success(self, get_context_root_passenger_id_mock, memory_queue_factory_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id"
        test_queue = Mock(spec=Queue)
        memory_queue_factory_mock.queue_with_id.return_value = test_queue
        test_serialized_event = "test_serialized_event"
        test_event = Mock(spec=Event, **{"passenger_name.return_value": "test_event"})
        test_event_consumer = Mock(spec=EventConsumer, **{"bus_stop_name.return_value": "test_event_consumer"})
        self.event_serializer_mock.serialize.return_value = test_serialized_event
        self.event_consumer_registry_mock.get_consumers_from_event.return_value = [test_event_consumer]

        self.process_event_bus.transport(test_event)

        self.event_serializer_mock.serialize.assert_called_once_with(test_event)
        test_queue.put.assert_called_once_with(test_serialized_event)
        self.event_consumer_registry_mock.get_consumers_from_event.assert_called_once_with("test_event")
        test_event.set_root_passenger_id.assert_called_once_with("test_root_passenger_id")
        memory_queue_factory_mock.queue_with_id.assert_called_once_with("test_event_consumer")
