from unittest import TestCase
from unittest.mock import Mock

from bus_station.shared_terminal.engine.engine import Engine
from bus_station.shared_terminal.engine.runner.self_process_engine_runner import SelfProcessEngineRunner


class TestSelfProcessEngineRunner(TestCase):
    def setUp(self) -> None:
        self.engine_mock = Mock(spec=Engine)
        self.engine_runner = SelfProcessEngineRunner(self.engine_mock)

    def test_run(self):
        self.engine_runner.run()

        self.engine_mock.start.assert_called_once_with()

    def test_stop(self):
        self.engine_runner.stop()

        self.engine_mock.stop.assert_called_once_with()
