from multiprocessing import Queue
from unittest import TestCase
from unittest.mock import Mock, call, MagicMock

from bus_station.passengers.middleware.passenger_middleware_executor import PassengerMiddlewareExecutor
from bus_station.passengers.passenger import Passenger
from bus_station.passengers.process_passenger_worker import ProcessPassengerWorker
from bus_station.passengers.serialization.passenger_deserializer import PassengerDeserializer
from bus_station.shared_terminal.bus_stop import BusStop


class TestProcessPassengerWorker(TestCase):
    def setUp(self) -> None:
        self.queue_get_mock = MagicMock()
        self.queue_mock = Mock(spec=Queue, get=self.queue_get_mock)
        self.passenger_bus_stop_mock = Mock(spec=BusStop)
        self.passenger_deserializer_mock = Mock(spec=PassengerDeserializer)
        self.passenger_middleware_executor_mock = Mock(spec=PassengerMiddlewareExecutor)
        self.process_passenger_worker = ProcessPassengerWorker(
            self.queue_mock,
            self.passenger_bus_stop_mock,
            self.passenger_middleware_executor_mock,
            self.passenger_deserializer_mock,
        )

    def test_work(self):
        test_item = "test_item"
        self.queue_mock.get.side_effect = [test_item, test_item, KeyboardInterrupt]
        test_passenger = Mock(spec=Passenger)
        self.passenger_deserializer_mock.deserialize.return_value = test_passenger

        self.process_passenger_worker.work()

        self.passenger_deserializer_mock.deserialize.assert_has_calls([call(test_item), call(test_item)])
        self.passenger_middleware_executor_mock.execute.assert_has_calls(
            [call(test_passenger, self.passenger_bus_stop_mock), call(test_passenger, self.passenger_bus_stop_mock)]
        )
        self.queue_mock.get.assert_has_calls([call(timeout=1.0), call(timeout=1.0), call(timeout=1.0)])
