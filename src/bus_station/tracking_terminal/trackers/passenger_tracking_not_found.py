class PassengerTrackingNotFound(Exception):
    def __init__(self, passenger_name: str, passenger_tracking_id: str):
        self.passenger_name = passenger_name
        self.passenger_tracking_id = passenger_tracking_id
        super().__init__(f"Passenger {passenger_name} with tracking id {passenger_tracking_id} not found")
