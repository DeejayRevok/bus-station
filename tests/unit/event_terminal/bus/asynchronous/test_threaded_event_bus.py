from threading import Thread
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.event_terminal.bus.asynchronous.threaded_event_bus import ThreadedEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware_executor import EventMiddlewareExecutor
from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry


class TestThreadedEventBus(TestCase):
    def setUp(self) -> None:
        self.event_registry_mock = Mock(spec=InMemoryRegistry)
        self.threaded_event_bus = ThreadedEventBus(self.event_registry_mock)

    @patch("bus_station.event_terminal.bus.event_bus.get_type_hints")
    def test_register_new_success(self, get_type_hints_mock):
        test_event = Mock(spec=Event)
        test_event_consumer = Mock(spec=EventConsumer)
        get_type_hints_mock.return_value = {"event": test_event.__class__}
        self.event_registry_mock.get_passenger_destination.return_value = None

        self.threaded_event_bus.register(test_event_consumer)

        self.event_registry_mock.register.assert_called_once_with(test_event.__class__, [test_event_consumer])

    @patch("bus_station.event_terminal.bus.event_bus.get_type_hints")
    def test_register_already_registered_success(self, get_type_hints_mock):
        test_event = Mock(spec=Event)
        test_event_consumer = Mock(spec=EventConsumer)
        get_type_hints_mock.return_value = {"event": test_event.__class__}
        test_event_consumers = [test_event_consumer]
        self.event_registry_mock.get_passenger_destination.return_value = test_event_consumers

        self.threaded_event_bus.register(test_event_consumer)

        self.assertCountEqual([test_event_consumer, test_event_consumer], test_event_consumers)

    @patch("bus_station.event_terminal.bus.event_bus.get_type_hints")
    @patch.object(EventMiddlewareExecutor, "execute")
    @patch("bus_station.event_terminal.bus.asynchronous.threaded_event_bus.Thread")
    def test_execute_success(self, thread_mock, middleware_executor_mock, get_type_hints_mock):
        test_event = Mock(spec=Event)
        test_event_consumer = Mock(spec=EventConsumer)
        get_type_hints_mock.return_value = {"event": test_event.__class__}
        test_thread = Mock(spec=Thread)
        thread_mock.return_value = test_thread
        self.event_registry_mock.get_passenger_destination.return_value = [test_event_consumer]

        self.threaded_event_bus.publish(test_event)

        thread_mock.assert_called_once_with(target=middleware_executor_mock, args=(test_event, test_event_consumer))
        test_thread.start.assert_called_once_with()
