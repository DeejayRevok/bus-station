class AddressNotFoundForPassenger(Exception):
    def __init__(self, passenger_name: str):
        self.passenger_name = passenger_name
        super().__init__(f"Address for passenger {passenger_name} not found")
