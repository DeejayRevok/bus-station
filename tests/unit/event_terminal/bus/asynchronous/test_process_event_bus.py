from multiprocessing.context import Process
from multiprocessing.queues import Queue
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.event_terminal.bus.asynchronous.process_event_bus import ProcessEventBus
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor
from bus_station.passengers.process_passenger_worker import ProcessPassengerWorker
from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.runnable import Runnable


class TestProcessEventBus(TestCase):
    def setUp(self) -> None:
        self.event_serializer_mock = Mock(spec=PassengerSerializer)
        self.event_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.middleware_executor_mock = Mock(spec=PassengerMiddlewareExecutor)
        self.event_registry_mock = Mock(spec=InMemoryRegistry)
        self.process_event_bus = ProcessEventBus(
            self.event_serializer_mock, self.event_deserializer_mock, self.event_registry_mock
        )
        self.process_event_bus._middleware_executor = self.middleware_executor_mock

    @patch("bus_station.event_terminal.bus.event_bus.get_type_hints")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.Process")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.Queue")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.ProcessPassengerWorker")
    def test_register_success_non_existing(self, worker_mock, queue_mock, process_mock, get_type_hints_mock):
        test_queue = Mock(spec=Queue)
        queue_mock.return_value = test_queue
        test_worker = Mock(spec=ProcessPassengerWorker)
        worker_mock.return_value = test_worker
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_event_consumer = Mock(spec=EventConsumer)
        test_event = Mock(spec=Event, name="TestEvent")
        get_type_hints_mock.return_value = {"event": test_event.__class__}
        test_serialized_event = "test_serialized_event"
        self.event_serializer_mock.serialize.return_value = test_serialized_event
        self.event_registry_mock.get_passenger_destination.return_value = None

        self.process_event_bus.register(test_event_consumer)

        queue_mock.assert_called_once_with()
        worker_mock.assert_called_once_with(
            test_queue,
            test_event_consumer,
            self.middleware_executor_mock,
            self.event_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_worker.work)
        self.event_registry_mock.get_passenger_destination.assert_called_once_with(test_event.__class__)
        self.event_registry_mock.register.assert_called_once_with(test_event.__class__, [test_queue])

    @patch("bus_station.event_terminal.bus.event_bus.get_type_hints")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.Process")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.Queue")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.ProcessPassengerWorker")
    def test_register_success_existing(self, worker_mock, queue_mock, process_mock, get_type_hints_mock):
        test_queue = Mock(spec=Queue)
        queue_mock.return_value = test_queue
        test_worker = Mock(spec=ProcessPassengerWorker)
        worker_mock.return_value = test_worker
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_event_consumer = Mock(spec=EventConsumer)
        test_event = Mock(spec=Event, name="TestEvent")
        get_type_hints_mock.return_value = {"event": test_event.__class__}
        test_serialized_event = "test_serialized_event"
        self.event_serializer_mock.serialize.return_value = test_serialized_event
        test_event_consumer_queues = [test_queue]
        self.event_registry_mock.get_passenger_destination.return_value = test_event_consumer_queues

        self.process_event_bus.register(test_event_consumer)

        queue_mock.assert_called_once_with()
        worker_mock.assert_called_once_with(
            test_queue,
            test_event_consumer,
            self.middleware_executor_mock,
            self.event_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_worker.work)
        self.event_registry_mock.get_passenger_destination.assert_called_once_with(test_event.__class__)
        self.assertCountEqual([test_queue, test_queue], test_event_consumer_queues)

    @patch.object(Runnable, "running")
    def test_execute_success(self, running_mock):
        running_mock.return_value = True
        test_queue = Mock(spec=Queue)
        test_event = Mock(spec=Event, name="TestEvent")
        test_serialized_event = "test_serialized_event"
        self.event_serializer_mock.serialize.return_value = test_serialized_event
        self.event_registry_mock.get_passenger_destination.return_value = [test_queue]

        self.process_event_bus.publish(test_event)

        self.event_serializer_mock.serialize.assert_called_once_with(test_event)
        test_queue.put.assert_called_once_with(test_serialized_event)
        self.event_registry_mock.get_passenger_destination.assert_called_once_with(test_event.__class__)

    @patch("bus_station.event_terminal.bus.event_bus.get_type_hints")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.Process")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.Queue")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.ProcessPassengerWorker")
    def test_start(self, worker_mock, queue_mock, process_mock, get_type_hints_mock):
        test_queue = Mock(spec=Queue)
        queue_mock.return_value = test_queue
        test_worker = Mock(spec=ProcessPassengerWorker)
        worker_mock.return_value = test_worker
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_event = Mock(spec=Event, name="TestCommand")
        get_type_hints_mock.return_value = {"event": test_event.__class__}
        test_event_consumer = Mock(spec=EventConsumer)
        self.event_registry_mock.get_passenger_destination.return_value = None
        self.process_event_bus.register(test_event_consumer)

        self.process_event_bus.start()

        queue_mock.assert_called_once_with()
        worker_mock.assert_called_once_with(
            test_queue,
            test_event_consumer,
            self.middleware_executor_mock,
            self.event_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_worker.work)
        test_process.start.assert_called_once_with()

    @patch("bus_station.event_terminal.bus.event_bus.get_type_hints")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.Process")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.Queue")
    @patch("bus_station.event_terminal.bus.asynchronous.process_event_bus.ProcessPassengerWorker")
    def test_stop(self, worker_mock, queue_mock, process_mock, get_type_hints_mock):
        test_queue = Mock(spec=Queue)
        queue_mock.return_value = test_queue
        test_worker = Mock(spec=ProcessPassengerWorker)
        worker_mock.return_value = test_worker
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_event = Mock(spec=Event, name="TestCommand")
        get_type_hints_mock.return_value = {"event": test_event.__class__}
        test_event_consumer = Mock(spec=EventConsumer)
        self.event_registry_mock.get_passenger_destination.return_value = None
        self.process_event_bus.register(test_event_consumer)

        self.process_event_bus.stop()

        queue_mock.assert_called_once_with()
        worker_mock.assert_called_once_with(
            test_queue,
            test_event_consumer,
            self.middleware_executor_mock,
            self.event_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_worker.work)
        test_worker.stop.assert_called_once_with()
        test_process.join.assert_called_once_with()
        test_queue.close.assert_called_once_with()
