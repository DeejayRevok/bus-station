from multiprocessing.context import Process
from multiprocessing.queues import Queue
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.event_terminal.bus.asynchronous.process_event_bus import ProcessEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.registry.in_memory_event_registry import InMemoryEventRegistry
from bus_station.passengers.process_passenger_worker import ProcessPassengerWorker
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.runnable import Runnable


class TestProcessEventBus(TestCase):
    def setUp(self) -> None:
        self.event_serializer_mock = Mock(spec=PassengerSerializer)
        self.event_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.event_registry_mock = Mock(spec=InMemoryEventRegistry)
        self.event_receiver_mock = Mock(spec=PassengerReceiver[Event, EventConsumer])
        self.process_event_bus = ProcessEventBus(
            self.event_serializer_mock, self.event_deserializer_mock, self.event_registry_mock, self.event_receiver_mock
        )

    @patch.object(Runnable, "running")
    def test_transport_success(self, running_mock):
        running_mock.return_value = True
        test_queue = Mock(spec=Queue)
        test_event = Mock(spec=Event, name="TestEvent")
        test_serialized_event = "test_serialized_event"
        self.event_serializer_mock.serialize.return_value = test_serialized_event
        self.event_registry_mock.get_event_destination_contacts.return_value = [test_queue]

        self.process_event_bus.transport(test_event)

        self.event_serializer_mock.serialize.assert_called_once_with(test_event)
        test_queue.put.assert_called_once_with(test_serialized_event)
        self.event_registry_mock.get_event_destination_contacts.assert_called_once_with(test_event.__class__)

    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.Process")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.ProcessPassengerWorker")
    def test_start(self, worker_mock, process_mock):
        test_queue = Mock(spec=Queue)
        test_worker = Mock(spec=ProcessPassengerWorker)
        worker_mock.return_value = test_worker
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_event = Mock(spec=Event, name="TestEvent")
        test_event_consumer = Mock(spec=EventConsumer)
        self.event_registry_mock.get_event_destination_contacts.return_value = [test_queue]
        self.event_registry_mock.get_event_destinations.return_value = [test_event_consumer]
        self.event_registry_mock.get_events_registered.return_value = [test_event.__class__]

        self.process_event_bus.start()

        worker_mock.assert_called_once_with(
            test_queue,
            test_event_consumer,
            self.event_receiver_mock,
            self.event_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_worker.work)
        test_process.start.assert_called_once_with()

    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.Process")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.ProcessPassengerWorker")
    def test_stop(self, worker_mock, process_mock):
        test_queue = Mock(spec=Queue)
        test_worker = Mock(spec=ProcessPassengerWorker)
        worker_mock.return_value = test_worker
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_event = Mock(spec=Event, name="TestEvent")
        test_event_consumer = Mock(spec=EventConsumer)
        self.event_registry_mock.get_event_destination_contacts.return_value = [test_queue]
        self.event_registry_mock.get_event_destinations.return_value = [test_event_consumer]
        self.event_registry_mock.get_events_registered.return_value = [test_event.__class__]
        self.process_event_bus.start()

        self.process_event_bus.stop()

        worker_mock.assert_called_once_with(
            test_queue,
            test_event_consumer,
            self.event_receiver_mock,
            self.event_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_worker.work)
        test_worker.stop.assert_called_once_with()
        test_process.join.assert_called_once_with()
