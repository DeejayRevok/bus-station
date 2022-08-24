class ContactNotFoundForEvent(Exception):
    def __init__(self, event_name: str):
        self.event_name = event_name
        super().__init__(f"Contact for event {event_name} not found")
