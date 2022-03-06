from dataclasses import dataclass

from redis import Redis

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.passengers.registry.in_memory_passenger_record_repository import InMemoryPassengerRecordRepository
from bus_station.passengers.registry.passenger_record import PassengerRecord
from bus_station.passengers.registry.redis_passenger_record_repository import RedisPassengerRecordRepository
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def handle(self, command: CommandTest) -> None:
        pass


class TestRedisPassengerRecordRepository(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_env_ready = False
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)
        cls.test_env_ready = True

    def setUp(self) -> None:
        self.in_memory_repository = InMemoryPassengerRecordRepository()
        self.redis_repository = RedisPassengerRecordRepository(self.redis_client, self.in_memory_repository)

    def tearDown(self) -> None:
        self.redis_repository.delete_by_passenger(CommandTest)

    def test_save(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        test_command_record = PassengerRecord(
            passenger=CommandTest,
            destination=test_command_handler,
            destination_contact=test_destination_contact
        )

        self.redis_repository.save(test_command_record)

        self.assertCountEqual([test_command_record], self.redis_repository.filter_by_passenger(CommandTest))

    def test_all(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        test_command_record = PassengerRecord(
            passenger=CommandTest,
            destination=test_command_handler,
            destination_contact=test_destination_contact
        )
        self.redis_repository.save(test_command_record)

        test_command_records = list(self.redis_repository.all())

        self.assertCountEqual([[test_command_record]], test_command_records)
