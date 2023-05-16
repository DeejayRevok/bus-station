from threading import Thread
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.event_terminal.bus.asynchronous.threaded_event_bus import ThreadedEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.event_consumer_registry import EventConsumerRegistry
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver


class TestThreadedEventBus(TestCase):
    def setUp(self) -> None:
        self.event_consumer_registry_mock = Mock(spec=EventConsumerRegistry)
        self.event_receiver_mock = Mock(spec=PassengerReceiver[Event, EventConsumer])
        self.threaded_event_bus = ThreadedEventBus(self.event_consumer_registry_mock, self.event_receiver_mock)

    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    @patch("bus_station.event_terminal.bus.asynchronous.threaded_event_bus.Thread")
    def test_transport_success(self, thread_mock, get_context_root_passenger_id_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id"
        test_event = Mock(spec=Event, **{"passenger_name.return_value": "test_event"})
        test_event_consumer = Mock(spec=EventConsumer)
        test_thread = Mock(spec=Thread)
        thread_mock.return_value = test_thread
        self.event_consumer_registry_mock.get_consumers_from_event.return_value = [test_event_consumer]

        self.threaded_event_bus.transport(test_event)

        thread_mock.assert_called_once_with(
            target=self.event_receiver_mock.receive, args=(test_event, test_event_consumer)
        )
        test_thread.start.assert_called_once_with()
        self.event_consumer_registry_mock.get_consumers_from_event.assert_called_once_with("test_event")
        test_event.set_root_passenger_id.assert_called_once_with("test_root_passenger_id")
