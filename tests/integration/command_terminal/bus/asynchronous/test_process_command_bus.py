from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Queue, Value
from time import sleep

from bus_station.command_terminal.bus.asynchronous.process_command_bus import ProcessCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.in_memory_command_registry import InMemoryCommandRegistry
from bus_station.passengers.passenger_class_resolver import PassengerClassResolver
from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.shared_terminal.fqn_getter import FQNGetter
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
        self.in_memory_repository = InMemoryPassengerRecordRepository()
        self.fqn_getter = FQNGetter()
        self.command_handler_resolver = InMemoryBusStopResolver(fqn_getter=self.fqn_getter)
        self.passenger_class_resolver = PassengerClassResolver()
        self.in_memory_registry = InMemoryCommandRegistry(
            in_memory_repository=self.in_memory_repository,
            command_handler_resolver=self.command_handler_resolver,
            fqn_getter=self.fqn_getter,
            passenger_class_resolver=self.passenger_class_resolver,
        )
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
        self.in_memory_registry.register(test_command_handler, self.command_queue)
        self.command_handler_resolver.add_bus_stop(test_command_handler)
        self.process_command_bus.start()

        self.process_command_bus.execute(test_command)

        sleep(1)
        self.assertEqual(1, test_command_handler.call_count.value)
