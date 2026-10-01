from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass
class FilterState:
    value: Any = None
    inverted: bool = False
    match: Any = None


@dataclasses.dataclass
class BrowserState:
    column_visibility: dict[str, bool] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class FilterBrowserState(BrowserState):
    splitter_sizes: tuple[int, ...] = ()
    filters: dict[str, FilterState] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FilterBrowserState:
        """Return the state from a serialized dictionary."""

        return cls(
            column_visibility=data.get('column_visibility', {}),
            splitter_sizes=tuple(data.get('splitter_sizes', ())),
            filters={
                key: FilterState(**value)
                for key, value in data.get('filters', {}).items()
            },
        )
