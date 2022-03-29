from unittest import TestCase

from bus_station.shared_terminal.broker_connection.connection_parameters.rabbitmq_connection_parameters import (
    RabbitMQConnectionParameters,
)


class TestRabbitMQConnectionParameters(TestCase):
    def test_get_connection_string_no_additional_args(self):
        test_host = "host"
        test_port = 1233
        test_username = "user"
        test_password = "password"
        test_vhost = "vhost"
        test_connection_parameters = RabbitMQConnectionParameters(
            test_host, test_port, test_username, test_password, test_vhost
        )

        connection_string = test_connection_parameters.get_connection_string()

        expected_connection_string = f"amqp://{test_username}:{test_password}@{test_host}:{test_port}/{test_vhost}"
        self.assertEqual(expected_connection_string, connection_string)

    def test_get_connection_string_additional_args(self):
        test_host = "host"
        test_port = 1233
        test_username = "user"
        test_password = "password"
        test_vhost = "vhost"
        test_additional_arg1 = "test_additional_arg1_value"
        test_additional_arg2 = "test_additional_arg2_value"
        test_connection_parameters = RabbitMQConnectionParameters(
            test_host,
            test_port,
            test_username,
            test_password,
            test_vhost,
            test_additional_arg1=test_additional_arg1,
            test_additional_arg2=test_additional_arg2,
        )

        connection_string = test_connection_parameters.get_connection_string()

        expected_connection_string = (
            f"amqp://{test_username}:{test_password}@{test_host}:{test_port}/{test_vhost}"
            f"?test_additional_arg1={test_additional_arg1}"
            f"&test_additional_arg2={test_additional_arg2}"
        )
        self.assertEqual(expected_connection_string, connection_string)
