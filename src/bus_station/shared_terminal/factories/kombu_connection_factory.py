from kombu.connection import Connection

from bus_station.shared_terminal.broker_connection.connection_parameters.connection_parameters import (
    ConnectionParameters,
)


class KombuConnectionFactory:
    def get_connection(self, broker_connection_parameters: ConnectionParameters) -> Connection:
        return Connection(broker_connection_parameters.get_connection_string())
