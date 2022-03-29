from multiprocessing.context import Process
from multiprocessing.queues import Queue
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.bus.asynchronous.process_command_bus import ProcessCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor
from bus_station.passengers.process_passenger_worker import ProcessPassengerWorker
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer
from bus_station.shared_terminal.runnable import Runnable


class TestProcessCommandBus(TestCase):
    def setUp(self) -> None:
        self.command_serializer_mock = Mock(spec=PassengerSerializer)
        self.command_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.middleware_executor_mock = Mock(spec=PassengerMiddlewareExecutor)
        self.command_registry_mock = Mock(spec=InMemoryCommandRegistry)
        self.process_command_bus = ProcessCommandBus(
            self.command_serializer_mock, self.command_deserializer_mock, self.command_registry_mock
        )
        self.process_command_bus._middleware_executor = self.middleware_executor_mock

    @patch.object(Runnable, "running")
    def test_execute_not_registered(self, running_mock):
        running_mock.return_value = True
        test_command = Mock(spec=Command)
        self.command_registry_mock.get_command_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            self.process_command_bus.execute(test_command)

        self.assertEqual(test_command.__class__.__name__, hnffc.exception.command_name)
        self.command_serializer_mock.serialize.assert_not_called()
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with(test_command.__class__)

    @patch.object(Runnable, "running")
    def test_execute_success(self, running_mock):
        running_mock.return_value = True
        test_queue = Mock(spec=Queue)
        test_serialized_command = "test_serialized_command"
        test_command = Mock(spec=Command)
        self.command_serializer_mock.serialize.return_value = test_serialized_command
        self.command_registry_mock.get_command_destination_contact.return_value = test_queue

        self.process_command_bus.execute(test_command)

        self.command_serializer_mock.serialize.assert_called_once_with(test_command)
        test_queue.put.assert_called_once_with(test_serialized_command)
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with(test_command.__class__)

    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.Process")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.ProcessPassengerWorker")
    def test_start(self, worker_mock, process_mock):
        test_queue = Mock(spec=Queue)
        test_worker = Mock(spec=ProcessPassengerWorker)
        worker_mock.return_value = test_worker
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_command = Mock(spec=Command)
        self.command_registry_mock.get_commands_registered.return_value = [test_command.__class__]
        test_command_handler = Mock(spec=CommandHandler)
        self.command_registry_mock.get_command_destination_contact.return_value = test_queue
        self.command_registry_mock.get_command_destination.return_value = test_command_handler

        self.process_command_bus.start()

        worker_mock.assert_called_once_with(
            test_queue,
            test_command_handler,
            self.middleware_executor_mock,
            self.command_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_worker.work)
        test_process.start.assert_called_once_with()

    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.Process")
    @patch("bus_station.command_terminal.bus.asynchronous.process_command_bus.ProcessPassengerWorker")
    def test_stop(self, worker_mock, process_mock):
        test_queue = Mock(spec=Queue)
        test_worker = Mock(spec=ProcessPassengerWorker)
        worker_mock.return_value = test_worker
        test_process = Mock(spec=Process)
        process_mock.return_value = test_process
        test_command = Mock(spec=Command)
        self.command_registry_mock.get_commands_registered.return_value = [test_command.__class__]
        test_command_handler = Mock(spec=CommandHandler)
        self.command_registry_mock.get_command_destination_contact.return_value = test_queue
        self.command_registry_mock.get_command_destination.return_value = test_command_handler
        self.process_command_bus.start()

        self.process_command_bus.stop()

        worker_mock.assert_called_once_with(
            test_queue,
            test_command_handler,
            self.middleware_executor_mock,
            self.command_deserializer_mock,
        )
        process_mock.assert_called_once_with(target=test_worker.work)
        test_worker.stop.assert_called_once_with()
        test_process.join.assert_called_once_with()
