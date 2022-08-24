from bus_station.shared_terminal.engine.engine import Engine
from bus_station.shared_terminal.engine.runner.self_process_engine_runner import SelfProcessEngineRunner
from tests.integration.integration_test_case import IntegrationTestCase


class TestNonBlockingEngine(Engine):
    def __init__(self):
        self.start_count = 0
        self.stop_count = 0

    def start(self) -> None:
        self.start_count += 1

    def stop(self) -> None:
        self.stop_count += 1


class TestSelfProcessEngineRunner(IntegrationTestCase):
    def setUp(self) -> None:
        self.test_engine = TestNonBlockingEngine()
        self.self_process_engine_runner = SelfProcessEngineRunner(self.test_engine)

    def test_run(self):
        self.self_process_engine_runner.run()

        self.assertEqual(1, self.test_engine.start_count)

    def test_stop(self):
        self.self_process_engine_runner.stop()

        self.assertEqual(1, self.test_engine.stop_count)
