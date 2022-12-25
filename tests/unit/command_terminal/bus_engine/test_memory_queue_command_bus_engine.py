from multiprocessing.queues import Queue
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine import MemoryQueueCommandBusEngine
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.command_registry import CommandRegistry
from bus_station.passengers.memory_queue_passenger_worker import MemoryQueuePassengerWorker
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer


class TestMemoryQueueCommandBusEngine(TestCase):
    def setUp(self) -> None:
        self.command_registry_mock = Mock(spec=CommandRegistry)
        self.command_receiver_mock = Mock(spec=PassengerReceiver)
        self.command_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.command_type_mock = Mock(spec=Command)

    @patch("bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine.MemoryQueuePassengerWorker")
    def test_init_handler_not_found(self, passenger_worker_builder):
        self.command_registry_mock.get_command_destination.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            MemoryQueueCommandBusEngine(
                self.command_registry_mock,
                self.command_receiver_mock,
                self.command_deserializer_mock,
                self.command_type_mock.__class__,
            )

        self.assertEqual("command.bus_station.command_terminal.command.Command", hnffc.exception.command_name)
        self.command_registry_mock.get_command_destination.assert_called_once_with(self.command_type_mock.__class__)
        passenger_worker_builder.assert_not_called()

    @patch("bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine.MemoryQueuePassengerWorker")
    def test_init_handler_found(self, passenger_worker_builder):
        memory_queue_passenger_worker_mock = Mock(spec=MemoryQueuePassengerWorker)
        passenger_worker_builder.return_value = memory_queue_passenger_worker_mock
        test_command_handler = Mock(spec=CommandHandler)
        test_queue = Mock(spec=Queue)
        self.command_registry_mock.get_command_destination.return_value = test_command_handler
        self.command_registry_mock.get_command_destination_contact.return_value = test_queue

        MemoryQueueCommandBusEngine(
            self.command_registry_mock,
            self.command_receiver_mock,
            self.command_deserializer_mock,
            self.command_type_mock.__class__,
        )

        self.command_registry_mock.get_command_destination.assert_called_once_with(self.command_type_mock.__class__)
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with(
            self.command_type_mock.__class__
        )
        passenger_worker_builder.assert_called_once_with(
            test_queue, test_command_handler, self.command_receiver_mock, self.command_deserializer_mock
        )

    @patch("bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine.MemoryQueuePassengerWorker")
    def test_start(self, passenger_worker_builder):
        memory_queue_passenger_worker_mock = Mock(spec=MemoryQueuePassengerWorker)
        passenger_worker_builder.return_value = memory_queue_passenger_worker_mock
        engine = MemoryQueueCommandBusEngine(
            self.command_registry_mock,
            self.command_receiver_mock,
            self.command_deserializer_mock,
            self.command_type_mock.__class__,
        )

        engine.start()

        memory_queue_passenger_worker_mock.work.assert_called_once_with()

    @patch("bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine.MemoryQueuePassengerWorker")
    def test_stop(self, passenger_worker_builder):
        memory_queue_passenger_worker_mock = Mock(spec=MemoryQueuePassengerWorker)
        passenger_worker_builder.return_value = memory_queue_passenger_worker_mock
        engine = MemoryQueueCommandBusEngine(
            self.command_registry_mock,
            self.command_receiver_mock,
            self.command_deserializer_mock,
            self.command_type_mock.__class__,
        )

        engine.stop()

        memory_queue_passenger_worker_mock.stop.assert_called_once_with()
