from multiprocessing.queues import Queue
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine import MemoryQueueCommandBusEngine
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.command_handler_not_found import CommandHandlerNotFound
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.passengers.memory_queue_passenger_worker import MemoryQueuePassengerWorker
from bus_station.passengers.reception.passenger_receiver import PassengerReceiver
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer


class TestMemoryQueueCommandBusEngine(TestCase):
    def setUp(self) -> None:
        self.command_handler_registry_mock = Mock(spec=CommandHandlerRegistry)
        self.command_receiver_mock = Mock(spec=PassengerReceiver)
        self.command_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.command_type_mock = Mock(spec=Command)

    @patch("bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine.MemoryQueuePassengerWorker")
    def test_init_handler_not_found(self, passenger_worker_builder):
        self.command_handler_registry_mock.get_bus_stop_by_name.return_value = None

        with self.assertRaises(CommandHandlerNotFound) as context:
            MemoryQueueCommandBusEngine(
                self.command_handler_registry_mock,
                self.command_receiver_mock,
                self.command_deserializer_mock,
                "test_command_handler",
            )

        self.assertEqual("test_command_handler", context.exception.command_handler_name)
        self.command_handler_registry_mock.get_bus_stop_by_name.assert_called_once_with("test_command_handler")
        passenger_worker_builder.assert_not_called()

    @patch("bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine.memory_queue_factory")
    @patch("bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine.MemoryQueuePassengerWorker")
    def test_init_handler_found(self, passenger_worker_builder, queue_factory_mock):
        test_command_handler = Mock(spec=CommandHandler)
        test_command_mock = Mock(spec=Command)
        test_command_mock.passenger_name.return_value = "test_command"
        test_command_handler.passenger.return_value = test_command_mock
        memory_queue_passenger_worker_mock = Mock(spec=MemoryQueuePassengerWorker)
        passenger_worker_builder.return_value = memory_queue_passenger_worker_mock
        test_queue = Mock(spec=Queue)
        queue_factory_mock.queue_with_id.return_value = test_queue
        self.command_handler_registry_mock.get_bus_stop_by_name.return_value = test_command_handler

        MemoryQueueCommandBusEngine(
            self.command_handler_registry_mock,
            self.command_receiver_mock,
            self.command_deserializer_mock,
            "test_command_handler",
        )

        self.command_handler_registry_mock.get_bus_stop_by_name.assert_called_once_with("test_command_handler")
        queue_factory_mock.queue_with_id.assert_called_once_with("test_command")
        passenger_worker_builder.assert_called_once_with(
            test_queue, test_command_handler, self.command_receiver_mock, self.command_deserializer_mock
        )

    @patch("bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine.memory_queue_factory")
    @patch("bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine.MemoryQueuePassengerWorker")
    def test_start(self, passenger_worker_builder, *_):
        memory_queue_passenger_worker_mock = Mock(spec=MemoryQueuePassengerWorker)
        passenger_worker_builder.return_value = memory_queue_passenger_worker_mock
        engine = MemoryQueueCommandBusEngine(
            self.command_handler_registry_mock,
            self.command_receiver_mock,
            self.command_deserializer_mock,
            "test_command_handler",
        )

        engine.start()

        memory_queue_passenger_worker_mock.work.assert_called_once_with()

    @patch("bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine.memory_queue_factory")
    @patch("bus_station.command_terminal.bus_engine.memory_queue_command_bus_engine.MemoryQueuePassengerWorker")
    def test_stop(self, passenger_worker_builder, *_):
        memory_queue_passenger_worker_mock = Mock(spec=MemoryQueuePassengerWorker)
        passenger_worker_builder.return_value = memory_queue_passenger_worker_mock
        engine = MemoryQueueCommandBusEngine(
            self.command_handler_registry_mock,
            self.command_receiver_mock,
            self.command_deserializer_mock,
            "test_command_handler",
        )

        engine.stop()

        memory_queue_passenger_worker_mock.stop.assert_called_once_with()
