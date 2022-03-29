from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.event_terminal.bus.synchronous.sync_event_bus import SyncEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware_executor import EventMiddlewareExecutor
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry


class TestSyncEventBus(TestCase):
    def setUp(self) -> None:
        self.event_registry_mock = Mock(spec=InMemoryEventRegistry)
        self.sync_event_bus = SyncEventBus(self.event_registry_mock)

    @patch.object(EventMiddlewareExecutor, "execute")
    def test_execute_success(self, middleware_executor_mock):
        test_event = Mock(spec=Event)
        test_event_consumer = Mock(spec=EventConsumer)
        self.event_registry_mock.get_event_destination_contacts.return_value = [test_event_consumer]

        self.sync_event_bus.publish(test_event)

        middleware_executor_mock.assert_called_once_with(test_event, test_event_consumer)
        self.event_registry_mock.get_event_destination_contacts.assert_called_once_with(test_event.__class__)
