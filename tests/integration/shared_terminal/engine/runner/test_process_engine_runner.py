from ctypes import c_int
from multiprocessing import Value
from time import sleep

from bus_station.shared_terminal.engine.engine import Engine
from bus_station.shared_terminal.engine.runner.process_engine_runner import ProcessEngineRunner
from tests.integration.integration_test_case import IntegrationTestCase


class TestNonBlockingEngine(Engine):
    def __init__(self):
        self.start_count = Value(c_int, 0)
        self.stop_count = Value(c_int, 0)

    def start(self) -> None:
        self.start_count.value += 1

    def stop(self) -> None:
        self.stop_count.value += 1


class TestBlockingEngine(Engine):
    def __init__(self):
        self.start_count = Value(c_int, 0)
        self.stop_count = Value(c_int, 0)

    def start(self) -> None:
        self.start_count.value += 1
        while True:
            pass

    def stop(self) -> None:
        self.stop_count.value += 1


class TestNonInterruptProcessEngineRunner(IntegrationTestCase):
    def setUp(self) -> None:
        self.engine = TestNonBlockingEngine()
        self.process_engine_runner = ProcessEngineRunner(self.engine, False)

    def test_run(self):
        self.process_engine_runner.run()
        sleep(1)

        self.assertEqual(1, self.engine.start_count.value)

    def test_stop(self):
        self.process_engine_runner.stop()

        self.assertEqual(1, self.engine.stop_count.value)


class TestInterruptProcessEngineRunner(IntegrationTestCase):
    def setUp(self) -> None:
        self.engine = TestNonBlockingEngine()
        self.process_engine_runner = ProcessEngineRunner(self.engine, True)

    def test_run_and_stop(self):
        self.process_engine_runner.run()
        sleep(1)

        self.assertEqual(1, self.engine.start_count.value)

        self.process_engine_runner.stop()

        self.assertEqual(1, self.engine.stop_count.value)
