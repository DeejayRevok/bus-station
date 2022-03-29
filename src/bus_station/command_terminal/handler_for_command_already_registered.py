class HandlerForCommandAlreadyRegistered(Exception):
    def __init__(self, command_name: str):
        self.command_name = command_name
        super(HandlerForCommandAlreadyRegistered, self).__init__(
            f"Handler for command {command_name} already registered"
        )
