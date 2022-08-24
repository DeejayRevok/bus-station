import os
import signal
from multiprocessing import Process

from bus_station.shared_terminal.engine.engine import Engine
from bus_station.shared_terminal.engine.runner.engine_runner import EngineRunner


class ProcessEngineRunner(EngineRunner):
    def __init__(self, engine: Engine, should_interrupt: bool):
        super().__init__(engine)
        self.__process = Process(target=engine.start)
        self.__should_interrupt = should_interrupt

    def run(self) -> None:
        self.__process.start()

    def stop(self) -> None:
        self._engine.stop()
        if self.__process.is_alive() is False:
            return

        if self.__should_interrupt is True and (process_pid := self.__process.pid) is not None:
            os.kill(process_pid, signal.SIGINT)
        self.__process.join()
