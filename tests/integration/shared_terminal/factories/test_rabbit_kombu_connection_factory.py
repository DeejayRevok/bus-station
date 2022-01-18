from unittest import TestCase

import pytest

from bus_station.shared_terminal.broker_connection.connection_parameters.rabbitmq_connection_parameters import (
    RabbitMQConnectionParameters,
)
from bus_station.shared_terminal.factories.kombu_connection_factory import KombuConnectionFactory


@pytest.mark.usefixtures("rabbitmq")
class TestRabbitKombuConnectionFactory(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_env_ready = False
        cls.rabbit_user = cls.rabbitmq["user"]
        cls.rabbit_password = cls.rabbitmq["password"]
        cls.rabbit_host = cls.rabbitmq["host"]
        cls.rabbit_port = cls.rabbitmq["port"]
        cls.test_env_ready = True

    def setUp(self) -> None:
        if self.test_env_ready is False:
            self.fail("Test environment is not ready")
        self.kombu_connection_factory = KombuConnectionFactory()

    def test_get_valid_rabbitmq_connection(self):
        test_connection_params = RabbitMQConnectionParameters(
            self.rabbit_host, self.rabbit_port, self.rabbit_user, self.rabbit_password, "/"
        )

        kombu_connection = self.kombu_connection_factory.get_connection(test_connection_params)
        kombu_connection.connect()

        self.assertTrue(kombu_connection.connected)
