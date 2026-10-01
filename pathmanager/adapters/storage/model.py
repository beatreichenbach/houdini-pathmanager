import dataclasses
from typing import Any


@dataclasses.dataclass
class State:
    browser: dict[str, Any] = dataclasses.field(default_factory=dict)
