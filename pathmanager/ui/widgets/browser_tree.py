from __future__ import annotations

import enum
from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from qtpy import QtCore, QtGui, QtWidgets

from .browser_delegates import ImageDelegate, StyledItemDelegate
from .browser_fields import Field, ModelIndex, get_value, set_value
from .browser_filter import Filter

CheckState = QtCore.Qt.CheckState
ItemDataRole = QtCore.Qt.ItemDataRole

T = TypeVar('T')


class ElementModel(QtGui.QStandardItemModel, Generic[T]):
    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)

        self._group = None
        self._fields: list[Field[Any]] = []

    def clear(self) -> None:
        super().clear()
        # NOTE: Clearing the model also clears the headers.
        self.refresh_header()

    def setData(
        self,
        index: ModelIndex,
        value: object,
        role: int = ItemDataRole.EditRole,
    ) -> bool:
        result = super().setData(index, value, role)

        # Update an element when a user changes the data in the delegate.
        if role == ItemDataRole.EditRole and (element := self.element(index)):
            field = self._fields[index.column()]
            value = self.data(index, ItemDataRole.EditRole)
            set_value(element, field.name, value)
            self.refresh_index(index)

        return result

    def add_field(self, field: Field[Any]) -> None:
        self._fields.append(field)
        self.refresh_header()

    def remove_field(self, field: Field[Any]) -> None:
        if field in self._fields:
            column = self._fields.index(field)
            self.removeColumn(column)
            self._fields.remove(field)
            self.refresh_header()

    def fields(self) -> tuple[Field[Any], ...]:
        return tuple(self._fields)

    def clear_fields(self) -> None:
        self._fields = []

    def element(self, index: ModelIndex) -> T | None:
        data = self.data(index.sibling(index.row(), 0), ItemDataRole.UserRole)
        return data

    def elements(
        self, parent: QtCore.QModelIndex | None = None, recursive: bool = True
    ) -> tuple[T, ...]:
        """Return all elements of a parent recursively."""

        if parent is None:
            parent = QtCore.QModelIndex()
        elements: list[T] = []
        for row in range(self.rowCount(parent)):
            index = self.index(row, 0, parent)
            if index.isValid():
                data = index.data(ItemDataRole.UserRole)
                if data is not None:
                    elements.append(data)
                if recursive:
                    elements.extend(self.elements(index))
        return tuple(elements)

    def append_element(
        self,
        obj: object,
        parent: QtCore.QModelIndex | None = None,
    ) -> QtCore.QModelIndex:

        parent_item = self.itemFromIndex(parent) if parent else None
        if parent_item is None:
            parent_item = self.invisibleRootItem()

        items = []
        for field in self._fields:
            value = get_value(obj, field.name)
            item = field.create_item(value)
            items.append(item)

        if not items:
            return QtCore.QModelIndex()

        item = items[0]
        item.setData(obj, ItemDataRole.UserRole)
        parent_item.appendRow(items)
        return item.index()

    def remove_element(self, element: T) -> None:
        index = self.find_index(element)
        if not index:
            return

        # Re-parent child rows
        item = self.itemFromIndex(index)
        parent = item.parent()
        for row in range(item.rowCount()):
            items = [item.child(row, column) for column in range(item.columnCount())]
            parent.appendRow(items)

        self.removeRow(index.row())

    def checked_elements(
        self, parent: QtCore.QModelIndex | None = None
    ) -> tuple[T, ...]:
        """Return checked elements."""

        if parent is None:
            parent = QtCore.QModelIndex()
        elements: list[T] = []
        for row in range(self.rowCount(parent)):
            index = self.index(row, 0, parent)
            if index.isValid():
                item = self.itemFromIndex(index)
                data = index.data(ItemDataRole.UserRole)
                if (
                    data is not None
                    and item.isCheckable()
                    and item.checkState() == QtCore.Qt.CheckState.Checked
                ):
                    elements.append(data)
                elements.extend(self.elements(index))
        return tuple(elements)

    def set_checked_elements(
        self, elements: Sequence[T], parent: QtCore.QModelIndex | None = None
    ) -> None:
        """Set elements to be checked. This does not change other check states."""

        if parent is None:
            parent = QtCore.QModelIndex()
        for row in range(self.rowCount(parent)):
            index = self.index(row, 0, parent)
            if index.isValid():
                data = index.data(ItemDataRole.UserRole)
                item = self.itemFromIndex(index)
                if data in elements and item.isCheckable():
                    item.setCheckState(QtCore.Qt.CheckState.Checked)
                self.set_checked_elements(elements, index)

    def set_all_checked(
        self, checked: bool = True, parent: QtCore.QModelIndex | None = None
    ) -> None:
        """Set all elements to be checked."""

        if checked:
            state = CheckState.Checked
        else:
            state = CheckState.Unchecked

        if parent is None:
            parent = QtCore.QModelIndex()
        for row in range(self.rowCount(parent)):
            index = self.index(row, 0, parent)
            if index.isValid():
                item = self.itemFromIndex(index)
                if item.isCheckable():
                    item.setCheckState(state)
                self.set_all_checked(checked, index)

    def get_value(self, index: QtCore.QModelIndex) -> object:
        """Return the element's value from an index."""

        element = self.element(index)
        column = index.column()
        field = self._fields[column]
        value = get_value(element, field.name)
        return value

    def find_index(
        self,
        value: T,
        role: ItemDataRole = ItemDataRole.UserRole,
        parent: QtCore.QModelIndex | None = None,
    ) -> QtCore.QModelIndex:
        if parent is None:
            parent = QtCore.QModelIndex()
        index = QtCore.QModelIndex()
        for row in range(self.rowCount(parent)):
            index = self.index(row, 0, parent)
            if not index.isValid():
                continue
            if value == self.data(index, role):
                break
            index = self.find_index(value, role, index)
            if index.isValid():
                break
        return index

    def refresh_index(self, index: ModelIndex) -> None:
        """Refresh the DisplayRole of all items in the index's row."""

        element = self.element(index)
        for column, field in enumerate(self._fields):
            item_index = index.sibling(index.row(), column)
            value = get_value(element, field.name)
            field.refresh(value, item_index)

    def refresh_element(self, element: T) -> None:
        """Refresh the DisplayRole of all items in the element's row."""

        index = self.find_index(element)
        if index.isValid():
            self.refresh_index(index)

    def refresh_column(
        self, column: int, parent: QtCore.QModelIndex | None = None
    ) -> None:
        """Refresh the DisplayRole of all items in the column."""

        if parent is None:
            parent = QtCore.QModelIndex()

        field = self._fields[column]
        for row in range(self.rowCount(parent)):
            index = self.index(row, column, parent)
            if not index.isValid():
                continue
            element = self.element(index)
            if element:
                value = get_value(element, field.name)
                field.refresh(value, index)
            self.refresh_column(column, parent=index)

    def refresh_header(self) -> None:
        labels = [field.label for field in self._fields]
        self.setHorizontalHeaderLabels(labels)


class ProxyModel(QtCore.QSortFilterProxyModel):
    """
    QSortFilterProxyModel with 'autoAcceptChildRows' that has been added in Qt6.
    """

    _autoAcceptChildRows = False

    def autoAcceptChildRows(self) -> bool:
        return self._autoAcceptChildRows

    def setAutoAcceptChildRows(self, value: bool) -> None:
        self._autoAcceptChildRows = value

    def filterAcceptsRow(self, source_row: int, source_parent: ModelIndex) -> bool:
        if super().filterAcceptsRow(source_row, source_parent):
            return True
        if self.autoAcceptChildRows() and source_parent.isValid():
            source_row = source_parent.row()
            source_parent = source_parent.parent()
            return self.filterAcceptsRow(source_row, source_parent)
        return False


class FilterProxyModel(ProxyModel):
    class AcceptRule(enum.Enum):
        DEFAULT = None
        ALLOW_ALL = 1
        ALLOW_NONE = 2

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self.setFilterCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

        self._filters: dict[int, Filter[Any]] = {}
        self._sort_roles: dict[int, ItemDataRole] = {}
        self._accept_rule = FilterProxyModel.AcceptRule.DEFAULT

    def filterAcceptsRow(self, source_row: int, source_parent: ModelIndex) -> bool:
        if self._accept_rule == FilterProxyModel.AcceptRule.DEFAULT:
            pass
        elif self._accept_rule == FilterProxyModel.AcceptRule.ALLOW_ALL:
            return True
        elif self._accept_rule == FilterProxyModel.AcceptRule.ALLOW_NONE:
            return False

        if not super().filterAcceptsRow(source_row, source_parent):
            return False

        for column, field_filter in self._filters.items():
            if field_filter.match:
                index = self.sourceModel().index(source_row, column, source_parent)
                value = index.data(field_filter.role)
                if not field_filter.accepts(value):
                    return False
        return True

    def lessThan(self, source_left: ModelIndex, source_right: ModelIndex) -> bool:
        # NOTE: The default implementation only handles built-in types.
        left = source_left.data(self.sort_role(source_left.column()))
        right = source_right.data(self.sort_role(source_right.column()))
        try:
            return (left is None, left) < (right is None, right)
        except TypeError:
            return True

    def accept_rule(self) -> FilterProxyModel.AcceptRule:
        return self._accept_rule

    def set_accept_rule(self, accept_rule: FilterProxyModel.AcceptRule) -> None:
        if accept_rule != self._accept_rule:
            self._accept_rule = accept_rule
            self.invalidateFilter()

    def filter(self, column: int) -> Filter[Any] | None:
        return self._filters.get(column)

    def set_filter(self, column: int, filter_: Filter[Any]) -> None:
        self._filters[column] = filter_

    def set_filters(self, filters: dict[int, Filter[Any]]) -> None:
        self._filters = filters

    def remove_filter(self, column: int) -> None:
        if column in self._filters:
            del self._filters[column]

    def sort_role(self, column: int) -> int:
        role = self._sort_roles.get(column, ItemDataRole.DisplayRole)
        return role

    def set_sort_role(self, column: int, role: ItemDataRole) -> None:
        self._sort_roles[column] = role


class ElementTree(QtWidgets.QTreeView):
    selection_changed = QtCore.Signal()
    # The checked_changed Signal is disabled by default.
    # Set enable_checked_signal = True to enable it.
    checked_changed = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._checked = set()

        # Initialize QTreeView
        mode = QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        self.setSelectionMode(mode)
        behavior = QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        self.setSelectionBehavior(behavior)
        self.setSortingEnabled(True)

        # Parent the delegate to enable setModelData on selection
        delegate = StyledItemDelegate(parent=self)
        self.setItemDelegate(delegate)

        # Initialize Header
        header = self.header()
        header.setMinimumHeight(32)
        header.setTextElideMode(QtCore.Qt.TextElideMode.ElideRight)
        header.setStretchLastSection(True)
        header.sectionResized.connect(self._header_resized)

        # Only check when enabled for optimization
        self.enable_checked_signal = False

    def dataChanged(
        self,
        top_left: ModelIndex,
        bottom_right: ModelIndex,
        roles: Sequence[int] = (),
    ) -> None:
        is_checked_role = QtCore.Qt.ItemDataRole.CheckStateRole in roles
        if self.enable_checked_signal and is_checked_role:
            checked_indexes = tuple(item.index() for item in self.checked_items())
            checked = set(checked_indexes)
            try:
                changed = self._checked != checked
            except RuntimeError:
                # In case the items no longer exist in the model
                changed = True

            if changed:
                self._checked = checked
                self.checked_changed.emit()
        super().dataChanged(top_left, bottom_right, roles)

    def expandToDepth(self, depth: int) -> None:
        """
        Expand items up to a depth. If the depth is negative, expand relative to the
        leaf node.
        """

        # HACK: The built-in method does not seem to work. Maybe the ProxyModels?

        if depth > 0:
            self._expand_to_depth(depth, current_depth=0)
        elif depth < 0:
            self.expandAll()
            self._collapse_to_depth(depth)
        else:
            self.expandAll()

    def _expand_to_depth(
        self,
        depth: int,
        index: QtCore.QModelIndex | None = None,
        current_depth: int = 0,
    ) -> None:
        """Expand the index if the current_depth is above the detph."""

        if index is None:
            index = QtCore.QModelIndex()
        if current_depth > depth:
            return
        if index.isValid():
            self.expand(index)

        model = self.model()
        for row in range(model.rowCount(index)):
            child = model.index(row, 0, index)
            if child.isValid():
                self._expand_to_depth(
                    depth, index=child, current_depth=current_depth + 1
                )

    def _collapse_to_depth(
        self, depth: int, index: QtCore.QModelIndex | None = None
    ) -> int:
        """Return the depth of the index and collapse it if it is above the depth."""

        if index is None:
            index = QtCore.QModelIndex()
        current_depth = -1

        model = self.model()
        for row in range(model.rowCount(index)):
            child = model.index(row, 0, index)
            if child.isValid():
                child_depth = self._collapse_to_depth(depth, index=child)
                current_depth = min(current_depth, child_depth - 1)

        if current_depth >= depth and index.isValid():
            self.collapse(index)

        return current_depth

    def selectionChanged(
        self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection
    ) -> None:
        self.selection_changed.emit()
        super().selectionChanged(selected, deselected)

    def checked_items(
        self, parent: QtCore.QModelIndex | None = None
    ) -> tuple[QtGui.QStandardItem, ...]:
        """Return checked QStandardItems from the list."""

        items = []

        if parent is None:
            parent = QtCore.QModelIndex()

        model = self.model()
        if isinstance(model, QtCore.QSortFilterProxyModel):
            model = model.sourceModel()
        if isinstance(model, QtGui.QStandardItemModel):
            for row in range(model.rowCount(parent=parent)):
                index = model.index(row, 0, parent)
                if index.isValid():
                    items.extend(self.checked_items(parent=index))
                    item = model.itemFromIndex(index)
                    if item and item.checkState() == QtCore.Qt.CheckState.Checked:
                        items.append(item)
        return tuple(items)

    def resize_columns(self, padding: int = 8) -> None:
        """Resize columns with horizontal padding taking all rows into account."""

        model = self.model()
        if model and model.rowCount():
            self.expandAll()
            for column in range(model.columnCount()):
                # Using sizeHint keeps the last column narrow
                width = self.header().sectionSizeHint(column)
                width = max(width, self.sizeHintForColumn(column))
                width += padding
                self.setColumnWidth(column, width)
            self.collapseAll()

    def _header_resized(self, column: int, old: int, new: int) -> None:
        """Resize ImageDelegates when the header resized."""

        delegate = self.itemDelegateForColumn(column)
        if isinstance(delegate, ImageDelegate):
            delegate.set_width(new)
            if new < delegate.max_width():
                for row in range(self.model().rowCount()):
                    index = self.model().index(row, column)
                    delegate.sizeHintChanged.emit(index)
