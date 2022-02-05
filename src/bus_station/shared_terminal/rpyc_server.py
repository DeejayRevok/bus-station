from rpyc import ThreadedServer

from bus_station.shared_terminal.rpyc_service import RPyCService


class RPyCServer:
    def __init__(self, rpyc_service: RPyCService, host: str, port: int):
        self.__rpyc_service = rpyc_service
        self.__host = host
        self.__port = port

    def run(self) -> None:
        rpyc_server = ThreadedServer(
            self.__rpyc_service,
            hostname=self.__host,
            port=self.__port,
        )
        rpyc_server.start()
        rpyc_server.close()
