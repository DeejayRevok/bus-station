from typing import ClassVar

from rpyc import ThreadedServer

from bus_station.shared_terminal.rpyc_service import RPyCService


class RPyCServer:

    __SELF_HOST_ADDR: ClassVar[str] = "127.0.0.1"

    def __init__(self, rpyc_service: RPyCService, port: int):
        self.__rpyc_service = rpyc_service
        self.__port = port

    def run(self) -> None:
        rpyc_server = ThreadedServer(
            service=self.__rpyc_service,
            hostname=self.__SELF_HOST_ADDR,
            port=self.__port,
        )
        rpyc_server.start()
        rpyc_server.close()
