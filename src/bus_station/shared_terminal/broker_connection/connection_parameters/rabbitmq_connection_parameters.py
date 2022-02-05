from typing import ClassVar, Union, final
from urllib.parse import urlencode

from bus_station.shared_terminal.broker_connection.connection_parameters.connection_parameters import (
    ConnectionParameters,
)


@final
class RabbitMQConnectionParameters(ConnectionParameters):

    __CONNECTION_STRING_PATTERN: ClassVar[str] = "amqp://{username}:{password}@{host}:{port}/{vhost}"

    def __init__(self, host: str, port: Union[int, str], username: str, password: str, vhost: str, **additional_args):
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        self.__vhost = vhost
        self.__additional_args = additional_args

    def get_connection_string(self) -> str:
        base_connection_str = self.__CONNECTION_STRING_PATTERN.format(
            host=self.__host,
            port=self.__port,
            username=self.__username,
            password=self.__password,
            vhost=self.__vhost,
        )
        if self.__additional_args is None or len(self.__additional_args) == 0:
            return base_connection_str

        base_connection_str += "?"
        base_connection_str += urlencode(self.__additional_args)
        return base_connection_str
