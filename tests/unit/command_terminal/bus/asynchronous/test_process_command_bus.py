from multiprocessing.context import Process
from multiprocessing.queues import Queue
from typing import Callable
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.bus.asynchronous.process_command_bus import ProcessCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_for_command_already_registered import HandlerForCommandAlreadyRegistered
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor
from bus_station.passengers.process_passenger_worker import ProcessPassengerWorker
from bus_station.passengers.registry.in_memory_passenger_record_repository import InMemoryRegistry
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.runnable import Runnable


class TestProcessCommandBus(TestCase):
    def setUp(self) -> None:
        self.command_serializer_mock = Mock(spec=PassengerSerializer)
        self.command_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.middleware_executor_mock = Mock(spec=PassengerMiddlewareExecutor)
        self.command_registry_mock = Mock(spec=InMemoryRegistry)
        self.process_command_bus = ProcessCommandBus(
            self.command_serializer_mock, self.command_deserializer_mock, self.command_registry_mock
        )
        self.process_command_bus._middleware_executor = self.middleware_executor_mock

    @patch("bus_station.command_terminal.bus.command_bus.get_type_hints")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.Process")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.Queue")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.ProcessPassengerWorker")
    def test_register_already_registered(self, worker_mock, queue_mock, process_mock, get_type_hints_mock):
        test_command_handler = Mock(spec=CommandHandler)
        test_command = Mock(spec=Command)
        get_type_hints_mock.return_value = {"command": test_command.__class__}
        self.command_registry_mock.__contains__ = Mock(spec=Callable)
        self.command_registry_mock.__contains__.return_value = True

        with self.assertRaises(HandlerForCommandAlreadyRegistered) as hfcar:
            self.process_command_bus.register(test_command_handler)

        self.assertEqual(test_command.__class__.__name__, hfcar.exception.command_name)
        queue_mock.assert_not_called()
        worker_mock.assert_not_called()
        process_mock.assert_not_called()
        self.command_registry_mock.__contains__.assert_called_once_with(test_command.__class__)

    @patch("bus_station.command_terminal.bus.command_bus.get_type_hints")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.Process")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.Queue")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.ProcessPassengerWorker")
    def test_register_success(self, worker_mock, queue_mock, process_mock, get_type_hints_mock):
        test_queue = Mock(spec=Queue)
        queue_mock.return_value = test_queue
        test_worker = Mock(spec=ProcessPassengerWorker)
        worker_mock.return_value = test_worker
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_command_handler = Mock(spec=CommandHandler)
        test_command = Mock(spec=Command)
        get_type_hints_mock.return_value = {"command": test_command.__class__}
        self.command_registry_mock.__contains__ = Mock(spec=Callable)
        self.command_registry_mock.__contains__.return_value = False

        self.process_command_bus.register(test_command_handler)

        queue_mock.assert_called_once_with()
        worker_mock.assert_called_once_with(
            test_queue,
            test_command_handler,
            self.middleware_executor_mock,
            self.command_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_worker.work)
        self.command_registry_mock.__contains__.assert_called_once_with(test_command.__class__)
        self.command_registry_mock.register.assert_called_once_with(test_command.__class__, test_queue)

    @patch.object(Runnable, "running")
    def test_execute_not_registered(self, running_mock):
        running_mock.return_value = True
        test_command = Mock(spec=Command)
        self.command_registry_mock.get_passenger_destination.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            self.process_command_bus.execute(test_command)

        self.assertEqual(test_command.__class__.__name__, hnffc.exception.command_name)
        self.command_serializer_mock.serialize.assert_not_called()
        self.command_registry_mock.get_passenger_destination.assert_called_once_with(test_command.__class__)

    @patch.object(Runnable, "running")
    def test_execute_success(self, running_mock):
        running_mock.return_value = True
        test_queue = Mock(spec=Queue)
        test_serialized_command = "test_serialized_command"
        test_command = Mock(spec=Command)
        self.command_serializer_mock.serialize.return_value = test_serialized_command
        self.command_registry_mock.get_passenger_destination.return_value = test_queue

        self.process_command_bus.execute(test_command)

        self.command_serializer_mock.serialize.assert_called_once_with(test_command)
        test_queue.put.assert_called_once_with(test_serialized_command)
        self.command_registry_mock.get_passenger_destination.assert_called_once_with(test_command.__class__)

    @patch("bus_station.command_terminal.bus.command_bus.get_type_hints")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.Process")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.Queue")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.ProcessPassengerWorker")
    def test_start(self, worker_mock, queue_mock, process_mock, get_type_hints_mock):
        test_queue = Mock(spec=Queue)
        queue_mock.return_value = test_queue
        test_worker = Mock(spec=ProcessPassengerWorker)
        worker_mock.return_value = test_worker
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_command = Mock(spec=Command)
        get_type_hints_mock.return_value = {"command": test_command.__class__}
        test_command_handler = Mock(spec=CommandHandler)
        self.command_registry_mock.__contains__ = Mock(spec=Callable)
        self.command_registry_mock.__contains__.return_value = False

        self.process_command_bus.register(test_command_handler)
        self.process_command_bus.start()

        queue_mock.assert_called_once_with()
        worker_mock.assert_called_once_with(
            test_queue,
            test_command_handler,
            self.middleware_executor_mock,
            self.command_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_worker.work)
        test_process.start.assert_called_once_with()

    @patch("bus_station.command_terminal.bus.command_bus.get_type_hints")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.Process")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.Queue")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.ProcessPassengerWorker")
    def test_stop(self, worker_mock, queue_mock, process_mock, get_type_hints_mock):
        test_queue = Mock(spec=Queue)
        queue_mock.return_value = test_queue
        test_worker = Mock(spec=ProcessPassengerWorker)
        worker_mock.return_value = test_worker
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_command = Mock(spec=Command)
        get_type_hints_mock.return_value = {"command": test_command.__class__}
        test_command_handler = Mock(spec=CommandHandler)
        self.command_registry_mock.__contains__ = Mock(spec=Callable)
        self.command_registry_mock.__contains__.return_value = False

        self.process_command_bus.register(test_command_handler)
        self.process_command_bus.stop()

        queue_mock.assert_called_once_with()
        worker_mock.assert_called_once_with(
            test_queue,
            test_command_handler,
            self.middleware_executor_mock,
            self.command_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_worker.work)
        test_worker.stop.assert_called_once_with()
        test_process.join.assert_called_once_with()
        test_queue.close.assert_called_once_with()
