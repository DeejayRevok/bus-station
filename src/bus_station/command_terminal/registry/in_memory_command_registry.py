from typing import Any, Iterable, List, Optional, Tuple, Type

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.command_registry import CommandRegistry
from bus_station.passengers.registry.in_memory_passenger_record_repository import InMemoryPassengerRecordRepository
from bus_station.passengers.registry.passenger_record import PassengerRecord


class InMemoryCommandRegistry(CommandRegistry):
    def __init__(self, in_memory_repository: InMemoryPassengerRecordRepository):
        self.__in_memory_repository = in_memory_repository

    def _register(self, command: Type[Command], handler: CommandHandler, handler_contact: Any) -> None:
        self.__in_memory_repository.save(
            PassengerRecord(passenger=command, destination=handler, destination_contact=handler_contact)
        )

    def get_command_destination(self, command: Type[Command]) -> Optional[CommandHandler]:
        command_records: Optional[
            List[PassengerRecord[Command, CommandHandler]]
        ] = self.__in_memory_repository.filter_by_passenger(command)
        if command_records is None:
            return None

        return command_records[0].destination

    def get_command_destination_contact(self, command: Type[Command]) -> Optional[Any]:
        command_records: Optional[
            List[PassengerRecord[Command, CommandHandler]]
        ] = self.__in_memory_repository.filter_by_passenger(command)
        if command_records is None:
            return None
        return command_records[0].destination_contact

    def get_commands_registered(self) -> Iterable[Tuple[Type[Command], Optional[CommandHandler], Any]]:
        for command_records in self.__in_memory_repository.all():
            command_record: PassengerRecord[Command, CommandHandler] = command_records[0]
            yield command_record.passenger, command_record.destination, command_record.destination_contact

    def unregister(self, command: Type[Command]) -> None:
        self.__in_memory_repository.delete_by_passenger(command)
