from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Value, Queue
from time import sleep

from bus_station.command_terminal.bus.asynchronous.process_command_bus import ProcessCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def __init__(self):
        self.call_count = Value(c_int, 0)

    def handle(self, command: CommandTest) -> None:
        self.call_count.value = self.call_count.value + 1


class TestProcessCommandBus(IntegrationTestCase):
    def setUp(self) -> None:
        self.passenger_serializer = PassengerJSONSerializer()
        self.passenger_deserializer = PassengerJSONDeserializer()
        self.in_memory_registry = InMemoryCommandRegistry()
        self.command_queue = Queue()
        self.process_command_bus = ProcessCommandBus(
            self.passenger_serializer, self.passenger_deserializer, self.in_memory_registry
        )

    def tearDown(self) -> None:
        self.process_command_bus.stop()
        self.command_queue.close()

    def test_execute_success(self):
        test_command = CommandTest()
        test_command_handler = CommandTestHandler()
        self.in_memory_registry.register_destination(test_command_handler, self.command_queue)
        self.process_command_bus.start()

        self.process_command_bus.execute(test_command)

        sleep(1)
        self.assertEqual(1, test_command_handler.call_count.value)
