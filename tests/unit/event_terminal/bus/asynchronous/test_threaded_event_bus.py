from threading import Thread
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.event_terminal.bus.asynchronous.threaded_event_bus import ThreadedEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware_executor import EventMiddlewareExecutor
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry


class TestThreadedEventBus(TestCase):
    def setUp(self) -> None:
        self.event_registry_mock = Mock(spec=InMemoryEventRegistry)
        self.threaded_event_bus = ThreadedEventBus(self.event_registry_mock)

    @patch.object(EventMiddlewareExecutor, "execute")
    @patch("bus_station.event_terminal.bus.asynchronous.threaded_event_bus.Thread")
    def test_execute_success(self, thread_mock, middleware_executor_mock):
        test_event = Mock(spec=Event)
        test_event_consumer = Mock(spec=EventConsumer)
        test_thread = Mock(spec=Thread)
        thread_mock.return_value = test_thread
        self.event_registry_mock.get_event_destination_contacts.return_value = [test_event_consumer]

        self.threaded_event_bus.publish(test_event)

        thread_mock.assert_called_once_with(target=middleware_executor_mock, args=(test_event, test_event_consumer))
        test_thread.start.assert_called_once_with()
        self.event_registry_mock.get_event_destination_contacts.assert_called_once_with(test_event.__class__)
