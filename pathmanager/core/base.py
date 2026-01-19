from abc import ABC

from pathmanager.core import schema


class Host(ABC):
    def get_items(self, selected: bool = False) -> tuple[schema.Item, ...]: ...
