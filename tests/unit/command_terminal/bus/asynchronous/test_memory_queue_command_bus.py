from multiprocessing.queues import Queue
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.command_terminal.bus.asynchronous.memory_queue_command_bus import MemoryQueueCommandBus
from bus_station.command_terminal.command import Command
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class TestMemoryQueueCommandBus(TestCase):
    def setUp(self) -> None:
        self.command_serializer_mock = Mock(spec=PassengerSerializer)
        self.process_command_bus = MemoryQueueCommandBus(
            self.command_serializer_mock,
        )

    @patch("bus_station.command_terminal.bus.asynchronous.memory_queue_command_bus.memory_queue_factory")
    @patch("bus_station.shared_terminal.bus.get_context_root_passenger_id")
    def test_transport_success(self, get_context_root_passenger_id_mock, memory_queue_factory_mock):
        get_context_root_passenger_id_mock.return_value = "test_root_passenger_id"
        test_queue = Mock(spec=Queue)
        memory_queue_factory_mock.queue_with_id.return_value = test_queue
        test_serialized_command = "test_serialized_command"
        test_command = Mock(spec=Command, **{"passenger_name.return_value": "test_command"})
        self.command_serializer_mock.serialize.return_value = test_serialized_command

        self.process_command_bus.transport(test_command)

        self.command_serializer_mock.serialize.assert_called_once_with(test_command)
        memory_queue_factory_mock.queue_with_id.assert_called_once_with("test_command")
        test_queue.put.assert_called_once_with(test_serialized_command)
        test_command.set_root_passenger_id.assert_called_once_with("test_root_passenger_id")
