from inspect import isclass
from typing import Any

__FQN_PATTERN = "{module_name}.{class_qualname}"


def resolve_fqn(subject: Any) -> str:
    cls = subject
    if not isclass(cls):
        cls = cls.__class__
    return __FQN_PATTERN.format(module_name=cls.__module__, class_qualname=cls.__qualname__)
