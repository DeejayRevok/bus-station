from bus_station.shared_terminal.engine.runner.engine_runner import EngineRunner


class SelfProcessEngineRunner(EngineRunner):
    def run(self) -> None:
        self._engine.start()

    def stop(self) -> None:
        self._engine.stop()
