from abc import ABC, abstractmethod


class BusStop(ABC):
    @classmethod
    @abstractmethod
    def bus_stop_name(cls) -> str:
        pass
