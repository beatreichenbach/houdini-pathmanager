from abc import ABC, abstractmethod
from collections.abc import Sequence

from . import schema


class Host(ABC):
    """Provide and update the items of a host application."""

    @abstractmethod
    def get_items(self, selected: bool = False) -> tuple[schema.Item, ...]:
        """Return the items of the host application."""

    @abstractmethod
    def update_items(self, items: Sequence[schema.Item]) -> None:
        """Update the host application with the item previews."""

    @staticmethod
    @abstractmethod
    def expand_string(text: str, expand_frame: bool = False) -> str:
        """Return the expanded string."""

    @staticmethod
    @abstractmethod
    def expand_files(path: str) -> tuple[str, ...]:
        """Return the files matching the path pattern."""
