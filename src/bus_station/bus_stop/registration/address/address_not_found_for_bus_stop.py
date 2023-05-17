class AddressNotFoundForBusStop(Exception):
    def __init__(self, bus_stop_id: str):
        self.bus_stop_id = bus_stop_id
        super().__init__(f"Address for bus stop {bus_stop_id} not found")
