class RunnableAlreadyRunningException(Exception):
    def __init__(self, runnable_name: str):
        self.runnable_name = runnable_name
        super().__init__(f"{runnable_name} is already running")
