from dataclasses import asdict
from typing import Any, Type, TypeVar

P = TypeVar("P")


class PassengerTrackingToProxyTransformer:
    def transform(self, tracking_instance: Any, target_proxy_class: Type[P]) -> P:
        target_proxy_data = asdict(tracking_instance)
        return target_proxy_class(**target_proxy_data)
