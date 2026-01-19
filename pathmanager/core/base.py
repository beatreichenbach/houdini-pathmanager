from abc import ABC
from collections.abc import Sequence

from pathmanager.core import schema


class Host(ABC):
    def get_items(self, selected: bool = False) -> tuple[schema.Item, ...]: ...

    def update_items(self, items: Sequence[schema.Item]) -> None: ...
