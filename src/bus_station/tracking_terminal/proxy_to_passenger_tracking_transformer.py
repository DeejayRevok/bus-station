from dataclasses import asdict
from typing import Any, Type, TypeVar

T = TypeVar("T")


class ProxyToPassengerTrackingTransformer:
    def transform(self, proxy_instance: Any, target_class: Type[T]) -> T:
        target_instance_data = asdict(proxy_instance)
        return target_class(**target_instance_data)
