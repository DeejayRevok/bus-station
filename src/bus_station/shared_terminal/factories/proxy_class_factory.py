from types import new_class
from typing import ClassVar, Type


class ProxyClassFactory:
    __PROXY_NAME_PATTERN: ClassVar[str] = "Proxy{target_class_name}"

    @classmethod
    def get_proxy(cls, target_class: Type) -> Type:
        proxy_name = cls.__PROXY_NAME_PATTERN.format(target_class_name=target_class.__name__)
        return new_class(proxy_name, bases=(target_class,))
