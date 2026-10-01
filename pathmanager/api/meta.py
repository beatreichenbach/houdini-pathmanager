from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import Any, Generic, TypeVar, cast

from qtpy import QtGui

from .. import utils
from ..qt_material_icons import MaterialIcon

ItemT = TypeVar('ItemT', bound='StyledItem')


class IterMeta(type, Generic[ItemT]):
    """A metaclass that turns class attributes into an ordered member registry."""

    _member_map: dict[str, ItemT]

    def __new__(
        mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]
    ) -> IterMeta[ItemT]:
        result: Any = super().__new__(mcls, name, bases, namespace)

        member_map: dict[str, ItemT] = {}
        for base in reversed(result.__mro__):
            for key, value in vars(base).items():
                if isinstance(value, StyledItem):
                    member_map[key] = cast(ItemT, value)

        result._member_map = member_map
        return result

    def __getitem__(cls, index: str | int) -> ItemT:
        if isinstance(index, int):
            return tuple(cls._member_map.values())[index]
        if isinstance(index, str):
            for key, value in cls._member_map.items():
                if index.casefold() == key.casefold():
                    return value
            for value in cls._member_map.values():
                if index.casefold() == value.name.casefold():
                    return value
        raise KeyError(index)

    def __contains__(cls, obj: object) -> bool:
        if isinstance(obj, StyledItem):
            return obj in cls._member_map.values()
        if isinstance(obj, str):
            return any(
                obj.casefold() in (key.casefold(), value.name.casefold())
                for key, value in cls._member_map.items()
            )
        return False

    def __iter__(cls) -> Iterator[ItemT]:
        return iter(cls._member_map.values())

    def __len__(cls) -> int:
        return len(cls._member_map)

    def get(cls, index: str | int) -> ItemT | None:
        try:
            return cls[index]
        except KeyError:
            return None


class IterItem:
    @property
    def items(self) -> Sequence:
        return ()


class Sortable:
    def __lt__(self, other: object) -> bool:
        if isinstance(other, Sortable):
            return cast(Any, self._sort_value) < cast(Any, other._sort_value)
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, Sortable):
            return cast(Any, self._sort_value) <= cast(Any, other._sort_value)
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Sortable):
            return cast(Any, self._sort_value) > cast(Any, other._sort_value)
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, Sortable):
            return cast(Any, self._sort_value) >= cast(Any, other._sort_value)
        return NotImplemented

    @property
    def _sort_value(self) -> object:
        return id(self)


class StyledItem(Sortable):
    def __init__(
        self, name: str, label: str = '', color: object = None, icon: object = None
    ) -> None:
        self.name = name
        self.label = label or utils.title(name)
        self._color: QtGui.QColor | None = None
        self._color_args = color
        self._icon: MaterialIcon | None = None
        self._icon_args = icon

    def __eq__(self, other: object) -> bool:
        return isinstance(other, StyledItem) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.label!r})'

    @property
    def _sort_value(self) -> object:
        return self.name

    def color(self) -> QtGui.QColor | None:
        if self._color is not None:
            return self._color

        args = cast(Any, self._color_args)
        if isinstance(args, QtGui.QColor):
            self._color = args
        elif isinstance(args, str):
            self._color = QtGui.QColor(args)
        elif isinstance(args, Mapping):
            self._color = QtGui.QColor(**args)
        elif isinstance(args, Iterable):
            self._color = QtGui.QColor(*args)
        elif args:
            self._color = QtGui.QColor(args)
        return self._color

    def icon(self) -> QtGui.QIcon | None:
        if self._icon is not None:
            return self._icon

        args = cast(Any, self._icon_args)
        if args:
            if isinstance(args, MaterialIcon):
                self._icon = args
            elif isinstance(args, str):
                self._icon = MaterialIcon(args)
            elif isinstance(args, Mapping):
                self._icon = MaterialIcon(**args)
            elif isinstance(args, Iterable):
                self._icon = MaterialIcon(*args)
            else:
                raise TypeError(f'unsupported icon definition: {args!r}')

        if self._icon is not None:
            color = self.color()
            if color is not None:
                self._icon.set_color(color)
        return self._icon


def format_styled_item(item: StyledItem | None) -> str:
    return item.label if isinstance(item, StyledItem) else 'Other'
