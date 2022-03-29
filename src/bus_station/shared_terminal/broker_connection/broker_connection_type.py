from enum import Enum
from typing import Type

from bus_station.shared_terminal.broker_connection.connection_parameters.rabbitmq_connection_parameters import (
    RabbitMQConnectionParameters,
)


class BrokerConnectionType(Enum):
    RABBITMQ = RabbitMQConnectionParameters

    def connection_parameters_cls(self) -> Type:
        return self.value
