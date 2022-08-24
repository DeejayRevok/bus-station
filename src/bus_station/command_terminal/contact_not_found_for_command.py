class ContactNotFoundForCommand(Exception):
    def __init__(self, command_name: str):
        self.command_name = command_name
        super().__init__(f"Contact for command {command_name} not found")
