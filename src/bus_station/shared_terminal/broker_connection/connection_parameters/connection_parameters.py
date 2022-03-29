from abc import abstractmethod
from typing import Protocol


class ConnectionParameters(Protocol):
    @abstractmethod
    def get_connection_string(self) -> str:
        pass
