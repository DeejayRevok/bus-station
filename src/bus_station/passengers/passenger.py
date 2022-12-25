from abc import abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Passenger:
    @classmethod
    @abstractmethod
    def passenger_name(cls) -> str:
        pass
