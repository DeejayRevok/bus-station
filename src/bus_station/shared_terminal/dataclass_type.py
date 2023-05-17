from typing import ClassVar, Dict, Protocol


class DataclassType(Protocol):
    __dataclass_fields__: ClassVar[Dict]
