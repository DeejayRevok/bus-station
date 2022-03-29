from bus_station.command_terminal.command import Command


class CommandExecutionFailed(Exception):
    def __init__(self, command: Command, reason: str):
        self.command = command
        self.reason = reason
        super().__init__(f"{command} execution has failed due to: {reason}")
