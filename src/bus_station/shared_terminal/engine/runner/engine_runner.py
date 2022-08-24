from abc import ABC, abstractmethod

from bus_station.shared_terminal.engine.engine import Engine


class EngineRunner(ABC):
    def __init__(self, engine: Engine):
        self._engine = engine

    def __enter__(self) -> None:
        self.run()

    def __exit__(self, _, __, ___) -> None:
        self.stop()

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
