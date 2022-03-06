from dataclasses import dataclass

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.passengers.registry.in_memory_passenger_record_repository import InMemoryPassengerRecordRepository
from bus_station.passengers.registry.passenger_record import PassengerRecord
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def handle(self, command: CommandTest) -> None:
        pass


class TestInMemoryPassengerRecordRepository(IntegrationTestCase):
    def setUp(self) -> None:
        self.in_memory_repository = InMemoryPassengerRecordRepository()

    def tearDown(self) -> None:
        self.in_memory_repository.delete_by_passenger(CommandTest)

    def test_save(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        test_command_record = PassengerRecord(
            passenger=CommandTest,
            destination=test_command_handler,
            destination_contact=test_destination_contact
        )

        self.in_memory_repository.save(test_command_record)

        self.assertCountEqual([test_command_record], self.in_memory_repository.filter_by_passenger(CommandTest))

    def test_all(self):
        test_command_handler = CommandTestHandler()
        test_destination_contact = "test_destination_contact"
        test_command_record = PassengerRecord(
            passenger=CommandTest,
            destination=test_command_handler,
            destination_contact=test_destination_contact
        )
        self.in_memory_repository.save(test_command_record)

        test_command_records = list(self.in_memory_repository.all())

        self.assertCountEqual([[test_command_record]], test_command_records)
