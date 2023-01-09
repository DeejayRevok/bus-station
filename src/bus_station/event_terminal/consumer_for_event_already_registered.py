class ConsumerForEventAlreadyRegistered(Exception):
    def __init__(self, consumer_name: str, event_name: str):
        self.consumer_name = consumer_name
        self.event_name = event_name
        super().__init__(f"Consumer {consumer_name} already registered for event {event_name}")
