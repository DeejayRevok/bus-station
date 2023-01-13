from unittest import TestCase
from unittest.mock import Mock

from bus_station.event_terminal.bus.synchronous.sync_event_bus import SyncEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver


class TestSyncEventBus(TestCase):
    def setUp(self) -> None:
        self.event_registry_mock = Mock(spec=InMemoryEventRegistry)
        self.event_receiver_mock = Mock(spec=PassengerReceiver[Event, EventConsumer])
        self.sync_event_bus = SyncEventBus(self.event_registry_mock, self.event_receiver_mock)

    def test_transport_success(self):
        test_event = Mock(spec=Event, **{"passenger_name.return_value": "test_event"})
        test_event_consumer = Mock(spec=EventConsumer)
        self.event_registry_mock.get_event_destination_contacts.return_value = [test_event_consumer]

        self.sync_event_bus.transport(test_event)

        self.event_receiver_mock.receive.assert_called_once_with(test_event, test_event_consumer)
        self.event_registry_mock.get_event_destination_contacts.assert_called_once_with("test_event")
