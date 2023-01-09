from dataclasses import dataclass

from redis import Redis

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.passengers.passenger_record.in_memory_passenger_record_repository import (
    InMemoryPassengerRecordRepository,
)
from bus_station.passengers.passenger_record.passenger_record import PassengerRecord
from bus_station.passengers.passenger_record.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.shared_terminal.fqn_getter import FQNGetter
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
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)
        cls.fqn_getter = FQNGetter()

    def setUp(self) -> None:
        self.in_memory_repository = InMemoryPassengerRecordRepository()
        self.redis_repository = RedisPassengerRecordRepository(self.redis_client)

    def tearDown(self) -> None:
        self.redis_repository.delete_by_passenger_name(CommandTest.passenger_name())

    def test_save(self):
        test_command_handler = CommandTestHandler()
        test_command_record = PassengerRecord(
            passenger_name=CommandTest.passenger_name(),
            passenger_fqn=self.fqn_getter.get(CommandTest),
            destination_name=CommandTestHandler.bus_stop_name(),
            destination_fqn=self.fqn_getter.get(test_command_handler),
            destination_contact="test_destination_contact",
        )

        self.redis_repository.save(test_command_record)

        self.assertCountEqual(
            [test_command_record], self.redis_repository.find_by_passenger_name(CommandTest.passenger_name())
        )

    def test_all(self):
        test_command_handler = CommandTestHandler()
        test_command_record = PassengerRecord(
            passenger_name=CommandTest.passenger_name(),
            passenger_fqn=self.fqn_getter.get(CommandTest),
            destination_name=CommandTestHandler.bus_stop_name(),
            destination_fqn=self.fqn_getter.get(test_command_handler),
            destination_contact="test_destination_contact",
        )
        self.redis_repository.save(test_command_record)

        test_command_records = list(self.redis_repository.all())

        self.assertCountEqual([test_command_record], test_command_records)
