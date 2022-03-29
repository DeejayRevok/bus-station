from inspect import isclass
from typing import Any, ClassVar


class FQNGetter:

    __FQN_PATTERN: ClassVar[str] = "{module_name}.{class_qualname}"

    def get(self, subject: Any) -> str:
        cls = subject
        if not isclass(cls):
            cls = cls.__class__
        return self.__FQN_PATTERN.format(module_name=cls.__module__, class_qualname=cls.__qualname__)
