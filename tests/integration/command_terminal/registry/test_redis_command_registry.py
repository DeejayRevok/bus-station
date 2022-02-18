from dataclasses import dataclass

from redis import Redis

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.redis_command_registry import RedisCommandRegistry
from bus_station.passengers.registry.destination_registration import DestinationRegistration
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def handle(self, command: CommandTest) -> None:
        pass


class TestRedisCommandRegistry(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_env_ready = False
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)
        cls.test_env_ready = True

    def setUp(self) -> None:
        self.redis_command_registry = RedisCommandRegistry(self.redis_client)

    def tearDown(self) -> None:
        self.redis_command_registry.unregister(CommandTest)

    def test_register_destination(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"

        self.redis_command_registry.register_destination(test_command_handler, test_destination_contact)

        expected_destination_registration = DestinationRegistration(
            destination=test_command_handler,
            destination_contact=test_destination_contact
        )
        self.assertEqual(expected_destination_registration,
                         self.redis_command_registry.get_passenger_destination_registration(CommandTest))

    def test_unregister(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        self.redis_command_registry.register_destination(test_command_handler, test_destination_contact)

        self.redis_command_registry.unregister(CommandTest)

        self.assertIsNone(self.redis_command_registry.get_passenger_destination_registration(CommandTest))

    def test_get_registered_passengers(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        self.redis_command_registry.register_destination(test_command_handler, test_destination_contact)

        registered_passengers = list(self.redis_command_registry.get_registered_passengers())

        expected_registered_passengers = [CommandTest]
        self.assertCountEqual(expected_registered_passengers, registered_passengers)
