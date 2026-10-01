from __future__ import annotations

import dataclasses
import enum
from functools import cache
from types import SimpleNamespace
from typing import Generic, TypeVar

from qtpy import QtCore, QtGui, QtWidgets

from pathmanager import utils
from pathmanager.api import schema
from pathmanager.qt_material_icons import MaterialIcon

CheckState = QtCore.Qt.CheckState
ItemDataRole = QtCore.Qt.ItemDataRole
ItemFlag = QtCore.Qt.ItemFlag

ModelIndex = QtCore.QModelIndex | QtCore.QPersistentModelIndex

ATTRIBUTE_SEPARATOR = '.'

T = TypeVar('T')


@dataclasses.dataclass
class Field(Generic[T]):
    name: str
    label: str = ''
    editable: bool = False
    checkable: bool = False

    def __post_init__(self) -> None:
        if not self.label:
            self.label = utils.title(self.name)

    def create_item(self, value: T) -> QtGui.QStandardItem:
        return self._create_item(value)

    def refresh(self, value: T, index: ModelIndex) -> None:
        self._set_display(value, index)

    def _create_item(self, display: object) -> QtGui.QStandardItem:
        item = QtGui.QStandardItem()
        flags = (
            ItemFlag.ItemIsEnabled
            | ItemFlag.ItemIsSelectable
            | ItemFlag.ItemIsDragEnabled
        )
        if self.editable:
            flags |= ItemFlag.ItemIsEditable
        if self.checkable:
            flags |= ItemFlag.ItemIsUserCheckable
            item.setCheckState(CheckState.Unchecked)
        item.setFlags(flags)
        item.setData(display, ItemDataRole.DisplayRole)
        return item

    @staticmethod
    def _set_display(display: object, index: ModelIndex) -> None:
        index.model().setData(index, display, ItemDataRole.DisplayRole)


class BoolField(Field[bool]):
    def create_item(self, value: bool) -> QtGui.QStandardItem:
        item = QtGui.QStandardItem()
        item.setFlags(ItemFlag.ItemIsEnabled | ItemFlag.ItemIsSelectable)
        if self.editable:
            item.setFlags(item.flags() or ItemFlag.ItemIsUserCheckable)
        item.setCheckState(CheckState.Checked if value else CheckState.Unchecked)
        item.setData(value, ItemDataRole.UserRole)
        return item

    def refresh(self, value: bool, index: ModelIndex) -> None:
        model = index.model()
        if isinstance(model, QtGui.QStandardItemModel):
            item = model.itemFromIndex(index)
            item.setCheckState(CheckState.Checked if value else CheckState.Unchecked)
        index.model().setData(index, value, ItemDataRole.UserRole)


class EnumField(Field[enum.Enum | None]):
    def create_item(self, value: enum.Enum | None) -> QtGui.QStandardItem:
        item = QtGui.QStandardItem()
        item.setFlags(ItemFlag.ItemIsEnabled | ItemFlag.ItemIsSelectable)
        if isinstance(value, enum.Enum):
            item.setData(value.value, ItemDataRole.DisplayRole)
        return item

    def refresh(self, value: enum.Enum | None, index: ModelIndex) -> None:
        display = value.value if isinstance(value, enum.Enum) else None
        index.model().setData(index, display, ItemDataRole.DisplayRole)


@dataclasses.dataclass
class ImageField(Field[str]):
    def create_item(self, value: str) -> QtGui.QStandardItem:
        item = QtGui.QStandardItem()
        item.setFlags(ItemFlag.ItemIsEnabled | ItemFlag.ItemIsSelectable)
        data: QtGui.QPixmap | str = value or get_default_thumbnail()
        item.setData(data, ItemDataRole.DecorationRole)
        return item

    def refresh(self, value: str, index: ModelIndex) -> None:
        data: QtGui.QPixmap | str = value or get_default_thumbnail()
        index.model().setData(index, data, ItemDataRole.DecorationRole)


@dataclasses.dataclass
class PathField(Field[schema.Item.Path]):
    def create_item(self, value: schema.Item.Path) -> QtGui.QStandardItem:
        text = value.raw if value is not None else ''
        tooltip = value.expanded if value is not None else ''
        item = self._create_item(text)
        item.setToolTip(tooltip)
        return item

    def refresh(self, value: schema.Item.Path, index: ModelIndex) -> None:
        text = value.raw if value is not None else ''
        tooltip = value.expanded if value is not None else ''
        self._set_display(text, index)
        index.model().setData(index, tooltip, ItemDataRole.ToolTipRole)


@dataclasses.dataclass
class PreviewField(Field[schema.Item.Preview]):
    def create_item(self, value: schema.Item.Preview) -> QtGui.QStandardItem:
        text = value.raw if value is not None else ''
        return self._create_item(text)

    def refresh(self, value: schema.Item.Preview, index: ModelIndex) -> None:
        text = value.raw if value is not None else ''
        self._set_display(text, index)


def get_value(obj: object, name: str) -> object:
    """
    Return the value from an object's attribute.
    Attribute name can be separated by a dot.
    """

    attributes = name.split(ATTRIBUTE_SEPARATOR) if name else ()
    value = obj
    for attribute in attributes:
        value = getattr(value, attribute, None)
    return value


def set_value(obj: object, name: str, value: object) -> None:
    """Set the attribute on an object, creating an object structure if needed."""

    if obj is None:
        return

    attributes = name.split(ATTRIBUTE_SEPARATOR)
    for attribute in attributes[:-1]:
        child = getattr(obj, attribute, None)
        if child is None:
            namespace = SimpleNamespace()
            setattr(obj, attribute, namespace)
            child = namespace
        obj = child
    setattr(obj, attributes[-1], value)


@cache
def get_default_thumbnail() -> QtGui.QPixmap:
    size = QtCore.QSize(192, 108)
    icon_size = QtCore.QSize(48, 48)

    pixmap = QtGui.QPixmap(size)
    palette = QtWidgets.QApplication.palette()
    color = palette.color(
        QtGui.QPalette.ColorGroup.Normal, QtGui.QPalette.ColorRole.Shadow
    )
    pixmap.fill(color)

    icon = MaterialIcon('image')
    icon_pixmap = icon.pixmap(size=icon_size, mode=QtGui.QIcon.Mode.Disabled)

    x = (size.width() - icon_size.width()) // 2
    y = (size.height() - icon_size.height()) // 2
    origin = QtCore.QPoint(x, y)

    painter = QtGui.QPainter(pixmap)
    painter.drawPixmap(origin, icon_pixmap)
    painter.end()
    return pixmap
