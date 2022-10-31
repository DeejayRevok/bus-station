class ContactNotFoundForConsumer(Exception):
    def __init__(self, event_consumer_name: str):
        self.event_consumer_name = event_consumer_name
        super().__init__(f"Contact for event consumer {event_consumer_name} not found")
