from __future__ import annotations

import sys
from collections import OrderedDict
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, Iterator, SupportsIndex, TypeVar

from qt_material_icons import MaterialIcon
from qtpy import QtGui

from pathmanager import utils

T_co = TypeVar('T_co', covariant=True)


class IterMeta(type):
    def __new__(cls, name, bases, classdict) -> Any:
        result = super().__new__(cls, name, bases, classdict)
        result._member_map = OrderedDict()
        for key, value in result.__dict__.items():
            if not key.startswith('_') and not callable(value):
                result._member_map[key] = value
        return result

    def __call__(cls, value, *args, **kwargs) -> Any:
        try:
            return cls.__getitem__(value)
        except KeyError:
            raise ValueError(f'{value!r} is not a valid {cls.__name__}')

    def __getitem__(cls, index: Any) -> Any:
        if isinstance(index, int):
            return list(cls._member_map.values())[index]
        elif isinstance(index, str):
            for key, value in cls._member_map.items():
                if index.casefold() == key.casefold():
                    return value
                elif isinstance(value, StyledItem):
                    if index in (value.name, value.label):
                        return value
        return cls._member_map[index]

    def __contains__(cls, obj) -> bool:
        return obj in cls._member_map.values()

    def __len__(cls) -> int:
        return len(cls._member_map)

    def __iter__(cls) -> Iterator[T_co]:
        return iter(cls._member_map.values())

    def __reversed__(cls) -> Iterator[T_co]:
        return tuple(cls).__reversed__()

    def get(cls, value) -> Any:
        try:
            return cls.__getitem__(value)
        except KeyError:
            return None

    def index(
        cls, x: Any, start: SupportsIndex = 0, stop: SupportsIndex = sys.maxsize
    ) -> int:
        return tuple(cls).index(x, start, stop)


class IterItem:
    @property
    def items(self) -> Sequence:
        return ()


class Sortable:
    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Sortable):
            return self._sort_value < other._sort_value
        return NotImplemented

    def __le__(self, other: Any) -> bool:
        if isinstance(other, Sortable):
            return self._sort_value <= other._sort_value
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, Sortable):
            return self._sort_value > other._sort_value
        return NotImplemented

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, Sortable):
            return self._sort_value >= other._sort_value
        return NotImplemented

    @property
    def _sort_value(self) -> Any:
        return id(self)


class StyledItem(Sortable):
    def __init__(
        self, name: str, label: str = '', color: Any = None, icon: Any = None
    ) -> None:
        self.name = name
        self.label = label or utils.title(name)
        self._color = None
        self._color_args = color
        self._icon = None
        self._icon_args = icon

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, StyledItem) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.label!r})'

    @property
    def _sort_value(self) -> Any:
        return self.name

    def color(self) -> QtGui.QColor | None:
        if not self._color:
            if isinstance(self._color_args, QtGui.QColor):
                self._color = self._color_args
            elif isinstance(self._color_args, str):
                self._color = QtGui.QColor(self._color_args)
            elif isinstance(self._color_args, Mapping):
                self._color = QtGui.QColor(**self._color_args)
            elif isinstance(self._color_args, Iterable):
                self._color = QtGui.QColor(*self._color_args)
            elif self._color_args:
                self._color = QtGui.QColor(self._color_args)
        return self._color

    def icon(self) -> QtGui.QIcon | None:
        if not self._icon:
            if isinstance(self._icon_args, QtGui.QIcon):
                self._icon = self._icon_args
            elif self._icon_args:
                if isinstance(self._icon_args, str):
                    self._icon = MaterialIcon(self._icon_args)
                elif isinstance(self._icon_args, Mapping):
                    self._icon = MaterialIcon(**self._icon_args)
                elif isinstance(self._icon_args, Iterable):
                    self._icon = MaterialIcon(*self._icon_args)
                if self._icon and self.color():
                    self._icon.set_color(self.color())
        return self._icon


def format_styled_item(item: StyledItem | None) -> str:
    return item.label if isinstance(item, StyledItem) else 'Other'
