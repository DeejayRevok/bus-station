from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Value
from time import sleep

from bus_station.command_terminal.bus.synchronous.distributed.rpyc_command_bus import RPyCCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.passengers.registry.redis_registry import RedisRegistry
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


class TestRPyCCommandBus(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_env_ready = False
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.test_env_ready = True

    def setUp(self) -> None:
        if self.test_env_ready is False:
            self.fail("Test environment is not ready")
        self.redis_registry = RedisRegistry(self.redis_host, self.redis_port)
        self.command_serializer = PassengerJSONSerializer()
        self.command_deserializer = PassengerJSONDeserializer()
        self.rpyc_command_bus = RPyCCommandBus(
            "localhost",
            1234,
            self.command_serializer,
            self.command_deserializer,
            self.redis_registry,
        )

    def tearDown(self) -> None:
        self.redis_registry.unregister(CommandTest)
        self.rpyc_command_bus.stop()

    def test_execute_success(self):
        test_command = CommandTest()
        test_command_handler = CommandTestHandler()
        self.rpyc_command_bus.register(test_command_handler)
        self.rpyc_command_bus.start()
        sleep(1)

        for i in range(10):
            self.rpyc_command_bus.execute(test_command)

            self.assertEqual(i + 1, test_command_handler.call_count.value)
