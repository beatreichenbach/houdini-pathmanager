from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from qtpy import QtCore, QtGui, QtWidgets

from . import meta
from .houdini import ComboParameter
from .widgets.filter import FilterState, MultiFilterWidget
from .widgets.tree import StyledItemDelegate


class StyledDelegate(StyledItemDelegate):
    use_color: bool = False
    use_icon: bool = True
    items: Sequence = ()

    def createEditor(
        self,
        parent: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> QtWidgets.QWidget:

        editor = StyledComboParameter(parent=parent)
        editor.set_use_icon(False)

        value = index.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)
        if isinstance(value, meta.IterItem):
            editor.set_items(value.items)
        elif self.items:
            editor.set_items(self.items)

        return editor

    def setEditorData(
        self, editor: StyledComboParameter, index: QtCore.QModelIndex
    ) -> None:
        value = index.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)
        editor.set_value(value)

    def setModelData(
        self,
        editor: StyledComboParameter,
        model: QtCore.QAbstractItemModel,
        index: QtCore.QModelIndex,
        value: Any = None,
    ) -> None:
        value = editor.value()
        super().setModelData(editor, model, index, value)

    def displayText(self, value: meta.StyledItem, locale: QtCore.QLocale) -> str:
        return value.label if value else ''

    def initStyleOption(
        self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex
    ) -> None:
        super().initStyleOption(option, index)
        if entity := index.data(QtCore.Qt.ItemDataRole.DisplayRole):
            if self.use_color and entity.color():
                option.palette.setColor(QtGui.QPalette.ColorRole.Text, entity.color())
            if self.use_icon and entity.icon():
                option.icon = entity.icon()
                option.features |= (
                    QtWidgets.QStyleOptionViewItem.ViewItemFeature.HasDecoration
                )


# class VersionNumberDelegate(StyledItemDelegate):
#     format: str = '{:03d}'
#
#     def __init__(self, new: bool = False, parent: QtCore.QObject | None = None) -> None:
#         super().__init__(parent)
#         self.new = new
#
#     def displayText(self, value: int, locale: QtCore.QLocale) -> str:
#         if value > 0:
#             return self.format.format(value)
#         if self.new:
#             return api.Statuses.NEW.label
#         return ''
#
#     def createEditor(
#         self,
#         parent: QtWidgets.QWidget,
#         option: QtWidgets.QStyleOptionViewItem,
#         index: QtCore.QModelIndex,
#     ) -> QtWidgets.QWidget:
#         value = index.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)
#         try:
#             value = int(value)
#         except (ValueError, TypeError):
#             value = 0
#
#         editor = IntParameter(parent=parent)
#         editor.set_line_min(0)
#         editor.set_slider_visible(False)
#         editor.set_default(value)
#
#         return editor
#
#     def setEditorData(self, editor: IntParameter, index: QtCore.QModelIndex) -> None:
#         value = index.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)
#         editor.set_value(value)
#
#     def setModelData(
#         self,
#         editor: IntParameter,
#         model: QtCore.QAbstractItemModel,
#         index: QtCore.QModelIndex,
#         value: Any = None,
#     ) -> None:
#         value = editor.value()
#         super().setModelData(editor, model, index, value)
#
#     def initStyleOption(
#         self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex
#     ) -> None:
#         super().initStyleOption(option, index)
#         if not self.new:
#             return
#         option.features |= QtWidgets.QStyleOptionViewItem.ViewItemFeature.HasDecoration
#         value = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
#         if isinstance(value, int) and value <= 0:
#             option.icon = api.Statuses.NEW.icon()


class StyledComboParameter(ComboParameter):
    _value: meta.StyledItem | None = None
    _default: meta.StyledItem | None = None
    _items: tuple[meta.StyledItem, ...] = ()
    _use_color: bool = False
    _use_icon: bool = True

    def _init_ui(self) -> None:
        super()._init_ui()
        self.combo.setMaxVisibleItems(20)

    def value(self) -> meta.StyledItem | None:
        return super().value()

    def set_value(self, value: meta.StyledItem | None) -> None:
        super().set_value(value)

    def items(self) -> tuple[meta.StyledItem, ...]:
        return self._items

    def set_items(self, items: Sequence[meta.StyledItem] | meta.IterMeta) -> None:
        if not isinstance(items, tuple):
            items = tuple(items)
        self._items = items
        self._update_items()
        default = items[0] if items else None
        self.set_default(default)

    def use_color(self) -> bool:
        return self._use_color

    def set_use_color(self, value: bool) -> None:
        if value != self._use_color:
            self._use_color = value
            self._update_items()

    def use_icon(self) -> bool:
        return self._use_icon

    def set_use_icon(self, value: bool) -> None:
        if value != self._use_icon:
            self._use_icon = value
            self._update_items()

    def _refresh_color(self) -> None:
        entity = self.combo.currentData()
        palette = self.palette()
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, entity.color())
        self.setPalette(palette)

    def _update_items(self) -> None:
        self.combo.blockSignals(True)
        for index in reversed(range(self.combo.count())):
            self.combo.removeItem(index)

        for entity in self._items:
            if entity is None:
                self.combo.addItem('')
            elif self._use_icon and entity.icon():
                self.combo.addItem(entity.icon(), entity.label, entity)
            else:
                self.combo.addItem(entity.label, entity)
            if self._use_color:
                i = self.combo.count() - 1
                color = entity.color()
                self.combo.setItemData(i, color, QtCore.Qt.ItemDataRole.ForegroundRole)
        self.combo.blockSignals(False)


class StyledFilterWidget(MultiFilterWidget):
    def __init__(
        self, title: str = '', parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(title, parent)

        self._use_color: bool = False
        self._use_icon: bool = True

    def state(self) -> FilterState:
        value = tuple(
            v.name for v in self._filter.value if isinstance(v, meta.StyledItem)
        )
        state = FilterState(value=value, inverted=self._filter.inverted)
        return state

    def set_state(self, state: FilterState) -> None:
        state.value = tuple(meta.StyledItem(v) for v in state.value)
        super().set_state(state)

    def use_color(self) -> bool:
        return self._use_color

    def set_use_color(self, value: bool) -> None:
        self._use_color = value
        self._update_checkboxes()

    def use_icon(self) -> bool:
        return self._use_icon

    def set_use_icon(self, value: bool) -> None:
        self._use_icon = value
        self._update_checkboxes()

    def _update_checkboxes(self) -> None:
        super()._update_checkboxes()

        for checkbox, value in zip(self._checkboxes, self._values):
            if isinstance(value, meta.StyledItem):
                checkbox.setText(value.label)
                if self._use_icon and value.icon():
                    checkbox.setIcon(value.icon())
                if self._use_color and value.color():
                    palette = checkbox.palette()
                    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, value.color())
                    self.setPalette(palette)
