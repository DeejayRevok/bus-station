class CommandHandlerNotFound(Exception):
    def __init__(self, command_handler_name: str):
        self.command_handler_name = command_handler_name
        super().__init__(f"Command handler {command_handler_name} not found")
