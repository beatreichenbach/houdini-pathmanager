from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Generic, TypeVar

from qtpy import QtCore, QtWidgets

T = TypeVar('T')


class RadioMenu(QtWidgets.QMenu, Generic[T]):
    selection_changed = QtCore.Signal(object)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self.action_group = QtWidgets.QActionGroup(self)

    def add_item(self, label: str, data: T, checked: bool = False) -> None:
        action = QtWidgets.QAction(self)
        action.setText(label)
        action.setCheckable(True)
        action.setData(data)

        self.action_group.addAction(action)
        action.setChecked(checked)
        action.triggered.connect(lambda: self.selection_changed.emit(data))

        self.addAction(action)

    def set_items(self, items: Mapping[str, T] | Sequence[T]) -> None:
        """
        Set the checkable items of the menu.

        If `items` is a Mapping type, it is expected to be in the form of {label: data}.
        """

        self.clear()

        if isinstance(items, Mapping):
            mapping = items
        else:
            mapping = {str(i): i for i in items}

        checked = True
        for label, data in mapping.items():
            self.add_item(label, data, checked)
            checked = False

    def selection(self) -> T | None:
        action = self.action_group.checkedAction()
        if action is None:
            return None
        return action.data()

    def set_selection(self, item: T) -> None:
        for action in self.actions():
            if action.isCheckable() and action.data() == item:
                action.setChecked(True)


class SelectionMenu(QtWidgets.QMenu, Generic[T]):
    selection_changed = QtCore.Signal(tuple)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self.addSeparator()

        action = QtWidgets.QAction(self)
        action.setText('Select All')
        action.triggered.connect(lambda: self._check_items(True))
        self.addAction(action)

        action = QtWidgets.QAction(self)
        action.setText('Select None')
        action.triggered.connect(lambda: self._check_items(False))
        self.addAction(action)

    def clear_items(self) -> None:
        for action in self.actions():
            if action.isCheckable():
                self.removeAction(action)

    def add_item(self, label: str, data: T, checked: bool = True) -> None:
        action = QtWidgets.QAction(self)
        action.setText(label)
        action.setCheckable(True)
        action.setChecked(checked)
        action.setData(data)
        action.triggered.connect(lambda: self._item_toggled())
        self.addAction(action)

    def set_items(self, items: Mapping[str, T] | Sequence[T]) -> None:
        """
        Set the checkable items of the menu.

        If `items` is a Mapping type, it is expected to be in the form of {label: data}.
        """

        self.clear_items()

        if isinstance(items, Mapping):
            mapping = items
        else:
            mapping = {str(i): i for i in items}

        for label, data in mapping.items():
            self.add_item(label, data)

    def selection(self) -> tuple[T, ...]:
        selection = tuple(a.data() for a in self.actions() if a.isChecked())
        return selection

    def set_selection(self, items: Sequence[T]) -> None:
        for action in self.actions():
            if action.isCheckable():
                action.setChecked(action.data() in items)

    def _check_items(self, checked: bool) -> None:
        for action in self.actions():
            if action.isCheckable():
                action.setChecked(checked)
        self._item_toggled()

    def _item_toggled(self) -> None:
        self.selection_changed.emit(self.selection())
