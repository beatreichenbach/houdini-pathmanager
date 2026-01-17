from abc import ABC

from pathmanager import schema


class Host(ABC):
    def get_items(self) -> tuple[schema.Item, ...]: ...
