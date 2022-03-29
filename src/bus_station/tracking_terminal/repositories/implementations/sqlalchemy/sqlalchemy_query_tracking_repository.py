from typing import Optional

from sqlalchemy.orm import Session

from bus_station.tracking_terminal.models.proxy_definitions import SAQueryTrackingProxy
from bus_station.tracking_terminal.models.query_tracking import QueryTracking
from bus_station.tracking_terminal.passenger_tracking_to_proxy_transformer import PassengerTrackingToProxyTransformer
from bus_station.tracking_terminal.proxy_to_passenger_tracking_transformer import ProxyToPassengerTrackingTransformer
from bus_station.tracking_terminal.repositories.query_tracking_repository import QueryTrackingRepository


class SQLAlchemyQueryTrackingRepository(QueryTrackingRepository):
    def __init__(
        self,
        sqlalchemy_session: Session,
        passenger_tracking_transformer: PassengerTrackingToProxyTransformer,
        proxy_transformer: ProxyToPassengerTrackingTransformer,
    ):
        self.__session = sqlalchemy_session
        self.__passenger_tracking_transformer = passenger_tracking_transformer
        self.__proxy_transformer = proxy_transformer

    def save(self, passenger_tracking: QueryTracking) -> None:
        proxy_instance = self.__passenger_tracking_transformer.transform(passenger_tracking, SAQueryTrackingProxy)
        self.__session.merge(proxy_instance)
        self.__session.commit()

    def find_by_id(self, passenger_tracking_id: str) -> Optional[QueryTracking]:
        proxy_instance = self.__session.query(SAQueryTrackingProxy).filter_by(id=passenger_tracking_id).one_or_none()
        if proxy_instance is None:
            return None
        return self.__proxy_transformer.transform(proxy_instance, QueryTracking)
