from abc import ABC, abstractmethod
from functools import wraps

from bus_station.shared_terminal.runnable_already_runnning_exception import RunnableAlreadyRunningException
from bus_station.shared_terminal.runnable_not_running_exception import RunnableNotRunningException


def is_running(func):
    @wraps(func)
    def checked_running(*args, **kwargs):
        if len(args) == 0 or not isinstance(args[0], Runnable):
            raise ValueError("is_running only applicable to Runnable instances")
        runnable = args[0]
        if runnable.running is False:
            raise RunnableNotRunningException(runnable.__class__.__name__)
        return func(*args, **kwargs)

    return checked_running


def is_not_running(func):
    @wraps(func)
    def checked_not_running(*args, **kwargs):
        if len(args) == 0 or not isinstance(args[0], Runnable):
            raise ValueError("is_not_running only applicable to Runnable instances")
        runnable = args[0]
        if runnable.running is True:
            raise RunnableAlreadyRunningException(runnable.__class__.__name__)
        return func(*args, **kwargs)

    return checked_not_running


class Runnable(ABC):
    def __init__(self):
        self.__running = False

    @property
    def running(self):
        return self.__running

    def start(self) -> None:
        self._start()
        self.__running = True

    @abstractmethod
    def _start(self) -> None:
        pass

    def stop(self) -> None:
        self._stop()
        self.__running = False

    @abstractmethod
    def _stop(self) -> None:
        pass
