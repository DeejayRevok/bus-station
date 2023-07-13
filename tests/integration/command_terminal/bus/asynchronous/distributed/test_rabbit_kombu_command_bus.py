import os
import signal
from ctypes import c_int
from dataclasses import dataclass
from multiprocessing import Process, Value
from time import sleep

from redis import Redis

from bus_station.command_terminal.bus.asynchronous.distributed.kombu_command_bus import KombuCommandBus
from bus_station.command_terminal.bus_engine.kombu_command_bus_engine import KombuCommandBusEngine
from bus_station.command_terminal.command import Command
from bus_station.command_terminal.command_handler import CommandHandler
from bus_station.command_terminal.command_handler_registry import CommandHandlerRegistry
from bus_station.command_terminal.middleware.command_middleware_receiver import CommandMiddlewareReceiver
from bus_station.passengers.serialization.passenger_json_deserializer import PassengerJSONDeserializer
from bus_station.passengers.serialization.passenger_json_serializer import PassengerJSONSerializer
from bus_station.shared_terminal.broker_connection.connection_parameters.rabbitmq_connection_parameters import (
    RabbitMQConnectionParameters,
)
from bus_station.shared_terminal.engine.runner.process_engine_runner import ProcessEngineRunner
from bus_station.shared_terminal.engine.runner.self_process_engine_runner import SelfProcessEngineRunner
from bus_station.shared_terminal.factories.kombu_connection_factory import KombuConnectionFactory
from tests.integration.integration_test_case import IntegrationTestCase


@dataclass(frozen=True)
class CommandTest(Command):
    pass


class CommandTestHandler(CommandHandler):
    def __init__(self):
        self.call_count = Value(c_int, 0)

    def handle(self, command: CommandTest) -> None:
        self.call_count.value = self.call_count.value + 1


class TestRabbitKombuCommandBus(IntegrationTestCase):
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
        cls.command_serializer = PassengerJSONSerializer()
        cls.command_deserializer = PassengerJSONDeserializer()
        cls.command_receiver = CommandMiddlewareReceiver()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.kombu_connection.release()

    def setUp(self) -> None:
        self.command_handler_registry = CommandHandlerRegistry()
        self.test_command_handler = CommandTestHandler()
        self.command_handler_registry.register(self.test_command_handler)
        self.kombu_command_bus_engine = KombuCommandBusEngine(
            self.kombu_connection,
            self.command_handler_registry,
            self.command_receiver,
            self.command_deserializer,
            self.test_command_handler.bus_stop_name(),
        )
        self.kombu_command_bus = KombuCommandBus(
            self.kombu_connection,
            self.command_serializer,
        )

    def tearDown(self) -> None:
        self.command_handler_registry.unregister(self.test_command_handler)

    def test_process_transport_success(self):
        test_command = CommandTest()
        with ProcessEngineRunner(engine=self.kombu_command_bus_engine, should_interrupt=False):
            self.kombu_command_bus.transport(test_command)

            sleep(1)
            self.assertEqual(1, self.test_command_handler.call_count.value)

    def test_self_process_engine_transport_success(self):
        test_command = CommandTest()
        engine_runner = SelfProcessEngineRunner(engine=self.kombu_command_bus_engine)
        runner_process = Process(target=engine_runner.run)
        runner_process.start()
        sleep(1)

        try:
            for i in range(10):
                self.kombu_command_bus.transport(test_command)

                sleep(1)
                self.assertEqual(i + 1, self.test_command_handler.call_count.value)
        finally:
            os.kill(runner_process.pid, signal.SIGINT)
