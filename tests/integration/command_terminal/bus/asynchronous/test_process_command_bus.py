from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Value
from time import sleep
from unittest import TestCase

from bus_station.command_terminal.bus.asynchronous.process_command_bus import ProcessCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.passengers.registry.in_memory_registry import InMemoryRegistry
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def __init__(self):
        self.call_count = Value(c_int, 0)

    def handle(self, command: CommandTest) -> None:
        self.call_count.value = self.call_count.value + 1


class TestProcessCommandBus(TestCase):
    def setUp(self) -> None:
        self.passenger_serializer = PassengerJSONSerializer()
        self.passenger_deserializer = PassengerJSONDeserializer()
        self.in_memory_registry = InMemoryRegistry()
        self.process_command_bus = ProcessCommandBus(
            self.passenger_serializer, self.passenger_deserializer, self.in_memory_registry
        )

    def tearDown(self) -> None:
        self.process_command_bus.stop()

    def test_execute_success(self):
        test_command = CommandTest()
        test_command_handler = CommandTestHandler()
        self.process_command_bus.register(test_command_handler)
        self.process_command_bus.start()

        self.process_command_bus.execute(test_command)

        sleep(1)
        self.assertEqual(1, test_command_handler.call_count.value)
