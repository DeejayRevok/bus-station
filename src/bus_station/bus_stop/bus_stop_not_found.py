class BusStopNotFound(Exception):
    def __init__(self, bus_stop_id: str):
        self.bus_stop_id = bus_stop_id
        super().__init__(f"Bus stop with id {bus_stop_id} not found")
