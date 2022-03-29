from unittest import TestCase
from unittest.mock import Mock

from bus_station.passengers.middleware.passenger_middleware import PassengerMiddleware
from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor
from bus_station.passengers.passenger import Passenger
from bus_station.shared_terminal.bus_stop import BusStop


class TestPassengerMiddlewareExecutor(TestCase):
    def setUp(self) -> None:
        self.passenger_middleware_executor = PassengerMiddlewareExecutor[Passenger, PassengerMiddleware, BusStop]()

    def test_add_middleware_definition_lazy(self):
        test_middleware_class = Mock(spec=PassengerMiddleware.__class__)
        test_arg = "test_arg"

        self.passenger_middleware_executor.add_middleware_definition(test_middleware_class, test_arg, lazy=True)

        test_middleware_class.assert_not_called()

    def test_add_middleware_definition_not_lazy(self):
        test_middleware_class = Mock(spec=PassengerMiddleware.__class__)
        test_arg = "test_arg"

        self.passenger_middleware_executor.add_middleware_definition(test_middleware_class, test_arg, lazy=False)

        test_middleware_class.assert_called_once_with(test_arg)
