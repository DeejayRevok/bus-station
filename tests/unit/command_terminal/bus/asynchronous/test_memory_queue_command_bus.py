from multiprocessing.queues import Queue
from unittest import TestCase
from unittest.mock import Mock

from bus_station.command_terminal.bus.asynchronous.memory_queue_command_bus import MemoryQueueCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.handler_not_found_for_command import HandlerNotFoundForCommand
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.passengers.serialization.passenger_serializer import PassengerSerializer


class TestMemoryQueueCommandBus(TestCase):
    def setUp(self) -> None:
        self.command_serializer_mock = Mock(spec=PassengerSerializer)
        self.command_registry_mock = Mock(spec=InMemoryCommandRegistry)
        self.process_command_bus = MemoryQueueCommandBus(
            self.command_serializer_mock,
            self.command_registry_mock,
        )

    def test_transport_not_registered(self):
        test_command = Mock(spec=Command)
        self.command_registry_mock.get_command_destination_contact.return_value = None

        with self.assertRaises(HandlerNotFoundForCommand) as hnffc:
            self.process_command_bus.transport(test_command)

        self.assertEqual(test_command.__class__.__name__, hnffc.exception.command_name)
        self.command_serializer_mock.serialize.assert_not_called()
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with(test_command.__class__)

    def test_transport_success(self):
        test_queue = Mock(spec=Queue)
        test_serialized_command = "test_serialized_command"
        test_command = Mock(spec=Command)
        self.command_serializer_mock.serialize.return_value = test_serialized_command
        self.command_registry_mock.get_command_destination_contact.return_value = test_queue

        self.process_command_bus.transport(test_command)

        self.command_serializer_mock.serialize.assert_called_once_with(test_command)
        test_queue.put.assert_called_once_with(test_serialized_command)
        self.command_registry_mock.get_command_destination_contact.assert_called_once_with(test_command.__class__)
