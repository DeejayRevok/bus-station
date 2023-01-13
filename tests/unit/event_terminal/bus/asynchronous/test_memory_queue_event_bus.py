from multiprocessing.queues import Queue
from unittest import TestCase
from unittest.mock import Mock

from bus_station.event_terminal.bus.asynchronous.memory_queue_event_bus import MemoryQueueEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class TestMemoryQueueEventBus(TestCase):
    def setUp(self) -> None:
        self.event_serializer_mock = Mock(spec=PassengerSerializer)
        self.event_registry_mock = Mock(spec=InMemoryEventRegistry)
        self.process_event_bus = MemoryQueueEventBus(
            self.event_serializer_mock,
            self.event_registry_mock,
        )

    def test_transport_success(self):
        test_queue = Mock(spec=Queue)
        test_serialized_event = "test_serialized_event"
        test_event = Mock(spec=Event, **{"passenger_name.return_value": "test_event"})
        self.event_serializer_mock.serialize.return_value = test_serialized_event
        self.event_registry_mock.get_event_destination_contacts.return_value = [test_queue]

        self.process_event_bus.transport(test_event)

        self.event_serializer_mock.serialize.assert_called_once_with(test_event)
        test_queue.put.assert_called_once_with(test_serialized_event)
        self.event_registry_mock.get_event_destination_contacts.assert_called_once_with("test_event")
