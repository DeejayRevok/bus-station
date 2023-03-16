from multiprocessing.queues import Queue
from unittest import TestCase
from unittest.mock import Mock, patch

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

    @patch("bus_station.shared_terminal.bus.get_distributed_id")
    def test_transport_sucess(self, get_distributed_id_mock):
        get_distributed_id_mock.return_value = "test_distributed_id"
        test_queue = Mock(spec=Queue)
        test_serialized_event = "test_serialized_event"
        test_event = Mock(spec=Event, **{"passenger_name.return_value": "test_event"})
        self.event_serializer_mock.serialize.return_value = test_serialized_event
        self.event_registry_mock.get_event_destination_contacts.return_value = [test_queue]

        self.process_event_bus.transport(test_event)

        self.event_serializer_mock.serialize.assert_called_once_with(test_event)
        test_queue.put.assert_called_once_with(test_serialized_event)
        self.event_registry_mock.get_event_destination_contacts.assert_called_once_with("test_event")
        test_event.set_distributed_id.assert_called_once_with("test_distributed_id")
