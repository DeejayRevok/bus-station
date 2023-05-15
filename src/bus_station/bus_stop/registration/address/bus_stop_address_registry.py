from abc import ABC, abstractmethod
from typing import Optional


class BusStopAddressRegistry(metaclass=ABC):
    @abstractmethod
    def register(self, bus_stop_id: str, address: str) -> None:
        pass

    @abstractmethod
    def get_bus_stop_address(self, bus_stop_id: str) -> Optional[str]:
        pass

    @abstractmethod
    def unregister(self, bus_stop_id: str) -> None:
        pass
