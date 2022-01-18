from unittest import TestCase

from bus_station.shared_terminal.runnable import Runnable, is_running, is_not_running
from bus_station.shared_terminal.runnable_already_runnning_exception import RunnableAlreadyRunningException
from bus_station.shared_terminal.runnable_not_running_exception import RunnableNotRunningException


class RunnableTest(Runnable):
    def __init__(self):
        super().__init__()
        self.count = 0

    def _start(self) -> None:
        pass

    def _stop(self) -> None:
        pass

    @is_running
    def test_running_method(self):
        self.count += 1

    @is_not_running
    def test_not_running_method(self):
        self.count -= 1


class TestRunnable(TestCase):
    def setUp(self) -> None:
        self.runnable = RunnableTest()

    def test_start_starts(self):
        self.runnable.start()

        self.assertTrue(self.runnable.running)

    def test_stop_stops(self):
        self.runnable.start()

        self.runnable.stop()

        self.assertFalse(self.runnable.running)

    def test_is_running_fails_if_not_running(self):
        with self.assertRaises(RunnableNotRunningException) as rnnrex:
            self.runnable.test_running_method()

            self.assertEqual(self.runnable.__class__.__name__, rnnrex.runnable_name)

    def test_is_not_running_fails_if_running(self):
        self.runnable.start()

        with self.assertRaises(RunnableAlreadyRunningException) as rarex:
            self.runnable.test_not_running_method()

            self.assertEqual(self.runnable.__class__.__name__, rarex.runnable_name)
