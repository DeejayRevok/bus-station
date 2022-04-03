from typing import Type

from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.shared_terminal.json_rpc_server import JsonRPCServer


class JsonRPCCommandServer(JsonRPCServer[Command, CommandHandler]):
    def _passenger_handler(
        self, bus_stop: CommandHandler, passenger_class: Type[Command], serialized_passenger: str
    ) -> None:
        command = self._passenger_deserializer.deserialize(serialized_passenger, passenger_cls=passenger_class)
        if not isinstance(command, Command):
            raise TypeError("Input serialized command is not a Command")
        self._passenger_receiver.receive(command, bus_stop)
