import signal
from multiprocessing import Process
from unittest import TestCase
from unittest.mock import Mock, patch

from bus_station.shared_terminal.engine.engine import Engine
from bus_station.shared_terminal.engine.runner.process_engine_runner import ProcessEngineRunner


class TestProcessEngineRunner(TestCase):
    def setUp(self) -> None:
        self.engine_mock = Mock(spec=Engine)

    @patch("bus_station.shared_terminal.engine.runner.process_engine_runner.Process")
    def test_run(self, process_builder_mock):
        process_mock = Mock(spec=Process)
        process_builder_mock.return_value = process_mock
        engine_runner = ProcessEngineRunner(self.engine_mock, False)

        engine_runner.run()

        process_builder_mock.assert_called_once_with(target=self.engine_mock.start)
        process_mock.start.assert_called_once_with()

    @patch("bus_station.shared_terminal.engine.runner.process_engine_runner.Process")
    def test_stop_process_not_alive(self, process_builder_mock):
        process_mock = Mock(spec=Process)
        process_mock.is_alive.return_value = False
        process_builder_mock.return_value = process_mock
        engine_runner = ProcessEngineRunner(self.engine_mock, False)

        engine_runner.stop()

        process_builder_mock.assert_called_once_with(target=self.engine_mock.start)
        process_mock.is_alive.assert_called_once_with()
        self.engine_mock.stop.assert_called_once_with()
        process_mock.join.assert_not_called()

    @patch("bus_station.shared_terminal.engine.runner.process_engine_runner.os")
    @patch("bus_station.shared_terminal.engine.runner.process_engine_runner.Process")
    def test_stop_process_alive_not_interrupt(self, process_builder_mock, os_mock):
        process_mock = Mock(spec=Process)
        process_mock.is_alive.return_value = True
        process_builder_mock.return_value = process_mock
        engine_runner = ProcessEngineRunner(self.engine_mock, False)

        engine_runner.stop()

        process_builder_mock.assert_called_once_with(target=self.engine_mock.start)
        process_mock.is_alive.assert_called_once_with()
        self.engine_mock.stop.assert_called_once_with()
        process_mock.join.assert_called_once_with()
        os_mock.kill.assert_not_called()

    @patch("bus_station.shared_terminal.engine.runner.process_engine_runner.os")
    @patch("bus_station.shared_terminal.engine.runner.process_engine_runner.Process")
    def test_stop_process_alive_interrupt(self, process_builder_mock, os_mock):
        process_mock = Mock(spec=Process)
        process_mock.is_alive.return_value = True
        test_pid = 2543
        process_mock.pid = test_pid
        process_builder_mock.return_value = process_mock
        engine_runner = ProcessEngineRunner(self.engine_mock, True)

        engine_runner.stop()

        process_builder_mock.assert_called_once_with(target=self.engine_mock.start)
        process_mock.is_alive.assert_called_once_with()
        self.engine_mock.stop.assert_called_once_with()
        os_mock.kill.assert_called_once_with(test_pid, signal.SIGINT)
        process_mock.join.assert_called_once_with()
