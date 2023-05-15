from abc import ABC, abstractmethod


class BusStopRegistrationSupervisor(ABC):
    @abstractmethod
    def on_register(self, bus_stop_id: str) -> None:
        pass

    @abstractmethod
    def on_unregister(self, bus_stop_id: str) -> None:
        pass
