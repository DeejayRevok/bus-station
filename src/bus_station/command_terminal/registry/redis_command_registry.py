from typing import Iterable, List, Optional, Tuple, Type

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.registry.remote_command_registry import RemoteCommandRegistry
from bus_station.passengers.registry.passenger_record import PassengerRecord
from bus_station.passengers.registry.redis_passenger_record_repository import RedisPassengerRecordRepository


class RedisCommandRegistry(RemoteCommandRegistry):
    def __init__(self, redis_repository: RedisPassengerRecordRepository):
        self.__redis_repository = redis_repository

    def _register(self, command: Type[Command], handler: CommandHandler, handler_contact: str) -> None:
        self.__redis_repository.save(
            PassengerRecord(passenger=command, destination=handler, destination_contact=handler_contact)
        )

    def get_command_destination_contact(self, command: Type[Command]) -> Optional[str]:
        command_records = self.__redis_repository.filter_by_passenger(command)
        if command_records is None:
            return None
        return command_records[0].destination_contact

    def get_commands_registered(self) -> Iterable[Tuple[Type[Command], CommandHandler, str]]:
        for command_records in self.__redis_repository.all():
            command_record = command_records[0]
            yield command_record.passenger, command_record.destination, command_record.destination_contact

    def get_command_destination(self, command: Type[Command]) -> Optional[CommandHandler]:
        command_records: Optional[
            List[PassengerRecord[Command, CommandHandler]]
        ] = self.__redis_repository.filter_by_passenger(command)
        if command_records is None:
            return None
        command_destination = command_records[0].destination
        return command_destination

    def unregister(self, command: Type[Command]) -> None:
        self.__redis_repository.delete_by_passenger(command)
