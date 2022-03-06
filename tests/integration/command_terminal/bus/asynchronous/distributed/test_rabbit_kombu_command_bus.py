from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Value
from time import sleep

from redis import Redis

from bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus import KombuCommandBus
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.redis_command_registry import RedisCommandRegistry
from bus_station.passengers.registry.in_memory_passenger_record_repository import InMemoryPassengerRecordRepository
from bus_station.passengers.registry.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.shared_terminal.broker_connection.connection_parameters.rabbitmq_connection_parameters import (
    RabbitMQConnectionParameters,
)
from bus_station.shared_terminal.factories.kombu_connection_factory import KombuConnectionFactory
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def __init__(self):
        self.call_count = Value(c_int, 0)

    def handle(self, command: CommandTest) -> None:
        self.call_count.value = self.call_count.value + 1


class TestRabbitKombuCommandBus(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_env_ready = False
        cls.rabbit_user = cls.rabbitmq["user"]
        cls.rabbit_password = cls.rabbitmq["password"]
        cls.rabbit_host = cls.rabbitmq["host"]
        cls.rabbit_port = cls.rabbitmq["port"]
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)
        cls.test_env_ready = True
        test_connection_params = RabbitMQConnectionParameters(
            cls.rabbit_host, cls.rabbit_port, cls.rabbit_user, cls.rabbit_password, "/"
        )
        kombu_connection_factory = KombuConnectionFactory()
        cls.kombu_connection = kombu_connection_factory.get_connection(test_connection_params)
        cls.kombu_connection.connect()

    def setUp(self) -> None:
        if self.test_env_ready is False:
            self.fail("Test environment is not ready")
        self.command_serializer = PassengerJSONSerializer()
        self.command_deserializer = PassengerJSONDeserializer()
        self.in_memory_repository = InMemoryPassengerRecordRepository()
        self.redis_repository = RedisPassengerRecordRepository(self.redis_client, self.in_memory_repository)
        self.redis_registry = RedisCommandRegistry(self.redis_repository)
        self.kombu_command_bus = KombuCommandBus(
            self.kombu_connection, self.command_serializer, self.command_deserializer, self.redis_registry
        )

    def tearDown(self) -> None:
        self.redis_registry.unregister(CommandTest)
        self.kombu_command_bus.stop()

    def test_execute_success(self):
        test_command = CommandTest()
        test_command_handler = CommandTestHandler()
        self.redis_registry.register(test_command_handler, test_command.__class__.__name__)
        self.kombu_command_bus.start()

        self.kombu_command_bus.execute(test_command)

        sleep(1)
        self.assertEqual(1, test_command_handler.call_count.value)
