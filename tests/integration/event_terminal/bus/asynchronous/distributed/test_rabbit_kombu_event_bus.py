import os
import signal
from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Process, Value
from time import sleep

from redis import Redis

from bus_station.event_terminal.bus.asynchronous.distributed.kombu_event_bus import KombuEventBus
from bus_station.event_terminal.bus_engine.kombu_event_bus_engine import KombuEventBusEngine
from bus_station.event_terminal.event import Event
from bus_station.event_terminal.event_consumer import EventConsumer
from bus_station.event_terminal.middleware.event_middleware_receiver import EventMiddlewareReceiver
from bus_station.event_terminal.registry.redis_event_registry import RedisEventRegistry
from bus_station.passengers.passenger_record.redis_passenger_record_repository import RedisPassengerRecordRepository
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.shared_terminal.broker_connection.connection_parameters.rabbitmq_connection_parameters import (
    RabbitMQConnectionParameters,
)
from bus_station.shared_terminal.bus_stop_resolver.in_memory_bus_stop_resolver import InMemoryBusStopResolver
from bus_station.shared_terminal.engine.runner.process_engine_runner import ProcessEngineRunner
from bus_station.shared_terminal.engine.runner.self_process_engine_runner import SelfProcessEngineRunner
from bus_station.shared_terminal.factories.kombu_connection_factory import KombuConnectionFactory
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class EventTest(Event):
    pass


class EventTestConsumer1(EventConsumer):
    def __init__(self):
        self.call_count = Value(c_int, 0)

    def consume(self, event: EventTest) -> None:
        self.call_count.value = self.call_count.value + 1


class EventTestConsumer2(EventConsumer):
    def __init__(self):
        self.call_count = Value(c_int, 2)

    def consume(self, event: EventTest) -> None:
        self.call_count.value = self.call_count.value - 1


class TestRabbitKombuEventBus(IntegrationTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rabbit_user = cls.rabbitmq["user"]
        cls.rabbit_password = cls.rabbitmq["password"]
        cls.rabbit_host = cls.rabbitmq["host"]
        cls.rabbit_port = cls.rabbitmq["port"]
        cls.redis_host = cls.redis["host"]
        cls.redis_port = cls.redis["port"]
        cls.redis_client = Redis(host=cls.redis_host, port=cls.redis_port)
        test_connection_params = RabbitMQConnectionParameters(
            cls.rabbit_host, cls.rabbit_port, cls.rabbit_user, cls.rabbit_password, "/"
        )
        kombu_connection_factory = KombuConnectionFactory()
        cls.kombu_connection = kombu_connection_factory.get_connection(test_connection_params)
        cls.kombu_connection.connect()

    def setUp(self) -> None:
        event_serializer = PassengerJSONSerializer()
        event_deserializer = PassengerJSONDeserializer()
        redis_repository = RedisPassengerRecordRepository(self.redis_client)
        event_consumer_resolver = InMemoryBusStopResolver[EventConsumer]()
        self.redis_registry = RedisEventRegistry(
            redis_repository=redis_repository,
            event_consumer_resolver=event_consumer_resolver,
        )
        event_middleware_receiver = EventMiddlewareReceiver()

        self.test_event_consumer1 = EventTestConsumer1()
        self.test_event_consumer2 = EventTestConsumer2()
        self.redis_registry.register(self.test_event_consumer1, EventTest.passenger_name())
        self.redis_registry.register(self.test_event_consumer2, EventTest.passenger_name())
        event_consumer_resolver.add_bus_stop(self.test_event_consumer1)
        event_consumer_resolver.add_bus_stop(self.test_event_consumer2)

        self.kombu_event_bus = KombuEventBus(
            self.kombu_connection,
            event_serializer,
            self.redis_registry,
        )
        self.kombu_event_bus_engine1 = KombuEventBusEngine(
            self.kombu_connection,
            self.redis_registry,
            event_middleware_receiver,
            event_deserializer,
            EventTest.passenger_name(),
            self.test_event_consumer1.bus_stop_name(),
        )
        self.kombu_event_bus_engine2 = KombuEventBusEngine(
            self.kombu_connection,
            self.redis_registry,
            event_middleware_receiver,
            event_deserializer,
            EventTest.passenger_name(),
            self.test_event_consumer2.bus_stop_name(),
        )

    def tearDown(self) -> None:
        self.redis_registry.unregister(EventTest.passenger_name())

    def test_process_transport_success(self):
        test_event = EventTest()
        with ProcessEngineRunner(self.kombu_event_bus_engine1, should_interrupt=False):
            with ProcessEngineRunner(self.kombu_event_bus_engine2, should_interrupt=False):
                for i in range(10):
                    self.kombu_event_bus.transport(test_event)

                    sleep(1)
                    self.assertEqual(i + 1, self.test_event_consumer1.call_count.value)
                    self.assertEqual(1 - i, self.test_event_consumer2.call_count.value)

    def test_self_process_transport_success(self):
        test_event = EventTest()
        engine_runner1 = SelfProcessEngineRunner(engine=self.kombu_event_bus_engine1)
        engine_runner2 = SelfProcessEngineRunner(engine=self.kombu_event_bus_engine2)
        runner_process1 = Process(target=engine_runner1.run)
        runner_process2 = Process(target=engine_runner2.run)
        runner_process1.start()
        runner_process2.start()

        try:
            for i in range(10):
                self.kombu_event_bus.transport(test_event)

                sleep(1)
                self.assertEqual(i + 1, self.test_event_consumer1.call_count.value)
                self.assertEqual(1 - i, self.test_event_consumer2.call_count.value)
        finally:
            os.kill(runner_process1.pid, signal.SIGINT)
            os.kill(runner_process2.pid, signal.SIGINT)
