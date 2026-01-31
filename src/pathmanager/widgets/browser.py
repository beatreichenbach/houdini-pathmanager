from __future__ import annotations

import dataclasses
from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import partial
from typing import Any

from qt_material_icons import MaterialIcon
from qtpy import QtCore, QtGui, QtWidgets

from pathmanager import utils
from pathmanager.widgets.filter import FilterListWidget, FilterState, FilterWidget
from .menu import RadioMenu, SelectionMenu
from .search import SearchLineEdit
from .tree import (
    ElementModel,
    ElementTree,
    Field,
    FilterProxyModel,
    get_value,
    set_value,
)

StateFlag = QtWidgets.QStyle.StateFlag
CheckState = QtCore.Qt.CheckState
ItemDataRole = QtCore.Qt.ItemDataRole
ItemFlag = QtCore.Qt.ItemFlag


@dataclass
class ColumnData:
    field: Field
    delegate: QtWidgets.QStyledItemDelegate | None = None
    filter_widget: FilterWidget | None = None
    visible: bool = True
    enabled: bool = True


class Container:
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}()'


@dataclasses.dataclass
class Group:
    name: str
    label: str = ''
    title: str = 'name'
    formatter: Callable = str

    def __post_init__(self) -> None:
        if not self.label:
            self.label = utils.title(self.name)


@dataclasses.dataclass
class Stack:
    name: str
    label: str = ''
    sort: str = ''
    order: QtCore.Qt.SortOrder = QtCore.Qt.SortOrder.DescendingOrder

    def __post_init__(self) -> None:
        if not self.label:
            self.label = utils.title(self.name)


@dataclasses.dataclass
class BrowserState:
    column_visibility: dict[str, bool] = dataclasses.field(default_factory=dict)


class Browser(QtWidgets.QWidget):
    double_clicked = QtCore.Signal(object)
    selection_changed = QtCore.Signal(object)
    model_expired = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._root_element = None
        self._columns: list[ColumnData] = []
        self._group: Group | None = None
        self._stack: Stack | None = None

        self._init_model()
        self._init_ui()
        self._init_columns_menu()

    def _init_model(self) -> None:
        self.model = ElementModel()
        # Force the disabled columns to be hidden
        self.model.columnsInserted.connect(self._refresh_columns)
        self.proxy = FilterProxyModel()
        self.proxy.setSourceModel(self.model)

    def _init_ui(self) -> None:
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)
        self._layout.setContentsMargins(QtCore.QMargins())

        self.tree = ElementTree()
        self.tree.setModel(self.proxy)
        self.tree.selection_changed.connect(self._selection_changed)
        self.tree.doubleClicked.connect(self._double_clicked)
        self._layout.addWidget(self.tree)

    def _init_columns_menu(self) -> None:
        self.columns_menu = ColumnMenu()
        self.columns_menu.set_columns(self._columns)
        self.columns_menu.selection_changed.connect(self._column_selection_changed)

        header = self.tree.header()
        header.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self._show_columns_menu)

    def clear(self) -> None:
        self.blockSignals(True)
        self.model.clear()
        # NOTE: Clearing the model refreshes the headers, so refresh_columns.
        self.refresh()
        self.blockSignals(False)

    def add_column(
        self,
        field: Field,
        delegate: QtWidgets.QStyledItemDelegate | None = None,
        filter_widget: FilterWidget | None = None,
        visible: bool = True,
        enabled: bool = True,
    ) -> None:
        column = len(self._columns)
        data = ColumnData(field, delegate, filter_widget, visible, enabled)
        self._columns.append(data)
        self.model.add_field(field)

        if delegate:
            delegate.setParent(self.tree)
            self.tree.setItemDelegateForColumn(column, delegate)

        if filter_widget and filter_widget.filter():
            self.proxy.set_filter(column, filter_widget.filter())

        self.set_column_visible(column, enabled and visible)
        self.columns_menu.set_columns(self._columns)

    def remove_column(self, column: int) -> None:
        self.proxy.remove_filter(column)
        if delegate := self.tree.itemDelegateForColumn(column):
            delegate.deleteLater()
        if column < len(self._columns):
            field = self._columns[column].field
            self.model.remove_field(field)
            self._columns.pop(column)
        self.columns_menu.set_columns(self._columns)

    def columns(self) -> tuple[ColumnData, ...]:
        return tuple(self._columns)

    def clear_columns(self) -> None:
        self._columns = []

    def root_element(self) -> Any:
        return self._root_element

    def set_root_element(self, element: Any) -> None:
        self._root_element = element

    def add_element(self, element: Any) -> None:
        """Add an element to the model."""

        self.model.append_element(element)
        self._refresh_hierarchy()

    def add_elements(self, elements: Sequence[Any]) -> None:
        """Add multiple elements to the model."""

        for element in elements:
            self.model.append_element(element)
        self._refresh_hierarchy()

    def elements(self, parent: QtCore.QModelIndex | None = None) -> tuple[Any, ...]:
        """Return only elements (without Containers)."""

        elements = tuple(
            e for e in self.model.elements(parent) if not isinstance(e, Container)
        )
        return elements

    def remove_element(self, element: Any) -> None:
        self.model.remove_element(element)
        self._refresh_hierarchy()

    def visible_elements(self, parent: QtCore.QModelIndex | None = None) -> tuple:
        """Return all elements visible in the ProxyModel."""

        if parent is None:
            parent = QtCore.QModelIndex()

        elements = []
        for row in range(self.proxy.rowCount(parent)):
            index = self.proxy.index(row, 0, parent)
            if index.isValid():
                source_index = self.proxy.mapToSource(index)
                element = self.model.element(source_index)
                if element is not None:
                    elements.append(element)
                elements.extend(self.visible_elements(parent=index))
        return tuple(elements)

    def selected_elements(self) -> tuple:
        elements = []
        indexes = self.tree.selectionModel().selectedRows()
        for index in indexes:
            model_index = self.proxy.mapToSource(index)
            elements.append(self.model.element(model_index))
        return tuple(elements)

    def set_selected_elements(self, elements: Sequence) -> None:
        selection_model = self.tree.selectionModel()
        selection_model.clearSelection()
        for element in elements:
            model_index = self.model.find_index(element)
            proxy_index = self.proxy.mapFromSource(model_index)
            command = (
                QtCore.QItemSelectionModel.SelectionFlag.Select
                | QtCore.QItemSelectionModel.SelectionFlag.Rows
            )
            selection_model.select(proxy_index, command)
            self.tree.expand(proxy_index)
            self.tree.scrollTo(proxy_index)

    def checked_elements(self, parent: QtCore.QModelIndex | None = None) -> tuple:
        """
        Return checked elements.
        This only returns elements that are visible in the current proxy.
        """

        if parent is None:
            parent = QtCore.QModelIndex()
        elements = []
        for row in range(self.proxy.rowCount(parent)):
            index = self.proxy.index(row, 0, parent)
            if index.isValid():
                model_index = self.proxy.mapToSource(index)
                data = model_index.data(ItemDataRole.UserRole)
                item = self.model.itemFromIndex(model_index)
                if (
                    data is not None
                    and item.isCheckable()
                    and item.checkState() == QtCore.Qt.CheckState.Checked
                ):
                    elements.append(data)
                elements.extend(self.checked_elements(index))
        return tuple(elements)

    def set_checked_elements(self, elements: Sequence) -> None:
        """Set elements to be checked. This does not change other check states."""

        self.tree.enable_checked_signal = False
        self.model.set_checked_elements(elements)
        self.tree.enable_checked_signal = True
        self.tree.checked_changed.emit()

    def set_selected_checked(self, checked: bool = True) -> None:
        """Set selected elements to be checked."""

        if checked:
            state = CheckState.Checked
        else:
            state = CheckState.Unchecked

        self.tree.enable_checked_signal = False
        indexes = self.tree.selectionModel().selectedRows()
        for index in indexes:
            model_index = self.proxy.mapToSource(index)
            item = self.model.itemFromIndex(model_index)
            if item.isCheckable():
                item.setCheckState(state)
        self.tree.enable_checked_signal = True
        self.tree.checked_changed.emit()

    def set_all_checked(self, checked: bool = True) -> None:
        """Set all elements to be checked."""

        self.tree.enable_checked_signal = False
        self.model.set_all_checked(checked)
        self.tree.enable_checked_signal = True
        self.tree.checked_changed.emit()

    def set_sort_order(self, order: QtCore.Qt.SortOrder) -> None:
        header = self.tree.header()
        column = header.sortIndicatorSection()
        if column < 0 or column >= header.count():
            column = 0
        self.tree.sortByColumn(column, order)

    def set_column_visible(self, column: int, visible: bool = True) -> None:
        """Set a column visible or hidden."""

        data = self._columns[column]
        data.visible = visible
        self.tree.setColumnHidden(column, not data.visible or not data.enabled)
        if data.visible and data.enabled:
            self.tree.resizeColumnToContents(column)

    def group(self) -> Group:
        return self._group

    def set_group(self, group: Group) -> None:
        self._group = group
        self._refresh_hierarchy()

    def stack(self) -> Stack:
        return self._stack

    def set_stack(self, stack: Stack) -> None:
        self._stack = stack
        self._refresh_hierarchy()

    def state(self) -> BrowserState:
        column_visibility = {c.field.name: c.visible for c in self._columns}
        state = BrowserState(column_visibility=column_visibility)
        return state

    def set_state(self, state: BrowserState) -> None:
        for column, data in enumerate(self._columns):
            visible = state.column_visibility.get(data.field.name, True)
            if not visible:
                self.set_column_visible(column, visible)

    def refresh(self) -> None:
        self._refresh_columns()
        self._refresh_palette()
        self.tree.resize_columns()
        if self._group:
            self.tree.expandToDepth(1)

    def _refresh_columns(self) -> None:
        """Refresh the columns, hiding disabled or hidden columns."""

        for column, data in enumerate(self._columns):
            self.set_column_visible(column, data.enabled and data.visible)

    def _refresh_palette(self, parent: QtGui.QStandardItem | None = None) -> None:
        """Refresh the palette, setting a different color for editable items."""

        palette = self.tree.palette()
        color = palette.color(QtGui.QPalette.ColorRole.PlaceholderText)
        brush = QtGui.QBrush(color)

        if parent is None:
            parent = self.model.invisibleRootItem()

        for row in range(parent.rowCount()):
            for col in range(parent.columnCount()):
                item = parent.child(row, col)
                if item and item.isEditable():
                    item.setForeground(brush)
                if item and col == 0:
                    self._refresh_palette(item)

    def _refresh_hierarchy(self) -> None:
        """Refresh the groups and stack hierarchy."""

        if self._group:
            self._update_group(self._group)
        else:
            self._reset_group()

        if self._stack:
            if self._group:
                for row in range(self.model.rowCount()):
                    index = self.model.index(row, 0)
                    self._update_stack(self._stack, index)
            else:
                self._update_stack(self._stack)

        self.refresh()

    def _reset_group(self) -> None:
        """Remove any groups."""

        elements = self.elements()
        self.model.clear()
        for element in elements:
            self.model.append_element(element)

    def _update_group(self, group: Group) -> None:
        """Update the groups."""

        elements = self.elements()

        # Create groups
        groups = defaultdict(list)
        for e in elements:
            value = get_value(e, group.name)
            groups[value].append(e)

        # Clear the model
        self.model.clear()

        # Append the groups
        for value, group_elements in groups.items():
            container = Container()
            set_value(container, group.title, group.formatter(value))
            index = self.model.append_element(container)
            standard_item = self.model.itemFromIndex(index)

            # Disable the Container
            for column in range(self.model.columnCount()):
                sibling = self.model.itemFromIndex(index.siblingAtColumn(column))
                sibling.setEnabled(False)
            standard_item.setCheckable(False)
            standard_item.setData(None, QtCore.Qt.ItemDataRole.CheckStateRole)

            for element in group_elements:
                self.model.append_element(element, index)

    def _update_stack(self, stack: Stack, parent: QtCore.QModelIndex | None = None):
        """Refresh the stacks for a parent."""

        elements = self.elements(parent)

        # Create stacks
        stacks = defaultdict(list)
        for e in elements:
            value = get_value(e, stack.name)
            stacks[value].append(e)

        # Clear the parent
        if parent is None:
            parent = QtCore.QModelIndex()
        for row in reversed(range(self.model.rowCount(parent))):
            self.model.removeRow(row, parent)

        # Append the stacks
        for stack_elements in stacks.values():
            reverse = stack.order == QtCore.Qt.SortOrder.AscendingOrder
            stack_elements.sort(key=lambda o: get_value(o, stack.sort), reverse=reverse)
            stack_iter = reversed(stack_elements)
            stack_index = self.model.append_element(next(stack_iter), parent)
            for e in stack_iter:
                self.model.append_element(e, stack_index)

    def _show_columns_menu(self, position: QtCore.QPoint) -> None:
        """Show the Fields menu."""

        self.columns_menu.exec_(self.tree.mapToGlobal(position))

    def _column_selection_changed(self, columns: Sequence[ColumnData]) -> None:
        """Handle selecting different Fields in the menu."""

        for column, data in enumerate(self._columns):
            visible = data in columns
            self.set_column_visible(column, visible)

    def _double_clicked(self, index: QtCore.QModelIndex) -> None:
        model_index = self.proxy.mapToSource(index)
        if element := self.model.element(model_index):
            if isinstance(element, Container):
                return
            self.double_clicked.emit(element)

    def _selection_changed(self) -> None:
        proxy_indexes = self.tree.selectionModel().selectedRows()
        indexes = tuple(self.proxy.mapToSource(index) for index in proxy_indexes)
        if indexes:
            element = self.model.element(indexes[0])
        else:
            element = None
        if isinstance(element, Container):
            return
        self.selection_changed.emit(element)

    def get_visible_elements(self, parent: QtCore.QModelIndex = None) -> tuple:
        elements = []
        for row in range(self.proxy.rowCount(parent)):
            if self.proxy.filterAcceptsRow(row, parent):
                index = self.proxy.index(row, 0, parent)
                if index.isValid():
                    data = index.data(ItemDataRole.UserRole)
                    if data is not None:
                        elements.append(data)
                    elements.extend(self.get_visible_elements(index))
        return tuple(elements)


@dataclasses.dataclass
class FilterBrowserState(BrowserState):
    splitter_sizes: tuple[int, ...] = ()
    filters: dict[str, FilterState] = dataclasses.field(default_factory=dict)


class FilterBrowser(Browser):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_toolbar()
        self._init_filters()

    def _init_ui(self) -> None:
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)
        self._layout.setContentsMargins(QtCore.QMargins())

        self.toolbar_layout = QtWidgets.QHBoxLayout()
        self._layout.addLayout(self.toolbar_layout)

        self.splitter = QtWidgets.QSplitter()
        self._layout.addWidget(self.splitter)
        self._layout.setStretch(1, 1)

        self.tree = ElementTree()
        self.tree.setAlternatingRowColors(True)
        self.tree.setModel(self.proxy)
        self.tree.selection_changed.connect(self._selection_changed)
        self.tree.doubleClicked.connect(self._double_clicked)
        self.splitter.addWidget(self.tree)

        self.filter_list = FilterListWidget()
        self.splitter.addWidget(self.filter_list)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setSizes((1, 0))
        self.splitter.splitterMoved.connect(self._splitter_moved)

    def _init_toolbar(self) -> None:
        self.toolbar = BrowserToolbar()
        self.toolbar.set_columns_menu(self.columns_menu)
        self.toolbar.sort_changed.connect(self.set_sort_order)
        self.toolbar.group_changed.connect(super().set_group)
        self.toolbar.stack_changed.connect(super().set_stack)
        self.toolbar.refreshed.connect(self.model_expired)
        self._layout.insertWidget(0, self.toolbar)

        # Stretch
        toolbar_layout = self.toolbar.layout()

        # Search
        self.search_line = SearchLineEdit()
        self.search_line.setMaximumWidth(256)
        self.search_line.textChanged.connect(self.proxy.setFilterWildcard)
        toolbar_layout.addWidget(self.search_line)

        # Filters
        icon = MaterialIcon('right_panel_open')
        icon_on = MaterialIcon('right_panel_close')
        color = self.palette().color(
            QtGui.QPalette.ColorGroup.Normal, QtGui.QPalette.ColorRole.Text
        )
        # TODO: push fix qt_material_icons
        icon.addPixmap(icon_on.pixmap(color=color), state=QtGui.QIcon.State.On)

        self.filter_button = QtWidgets.QToolButton()
        self.filter_button.setText('Filters')
        self.filter_button.setIcon(icon)
        self.filter_button.setCheckable(True)
        self.filter_button.toggled.connect(self.toggle_filter_list)
        toolbar_layout.addWidget(self.filter_button)

    def _init_filters(self) -> None:
        self.filter_list.set_model(self.model)
        self.filter_list.filter_changed.connect(self.proxy.invalidateFilter)

    def add_column(
        self,
        field: Field,
        delegate: QtWidgets.QStyledItemDelegate | None = None,
        filter_widget: FilterWidget | None = None,
        visible: bool = True,
        enabled: bool = True,
    ) -> None:
        super().add_column(
            field=field,
            delegate=delegate,
            filter_widget=filter_widget,
            visible=visible,
            enabled=enabled,
        )

        if filter_widget:
            column = len(self._columns) - 1
            self.filter_list.add_filter_widget(column, filter_widget)

    def set_group(self, group: Group | None) -> None:
        super().set_group(group)
        self.toolbar.set_group(group)

    def groups(self) -> tuple[Group, ...]:
        return self.toolbar.groups()

    def set_groups(self, groups: Sequence[Group]) -> None:
        self.toolbar.set_groups(groups)

    def set_stack(self, stack: Stack | None) -> None:
        super().set_stack(stack)
        self.toolbar.set_stack(stack)

    def stacks(self) -> tuple[Stack, ...]:
        return self.toolbar.stacks()

    def set_stacks(self, stacks: Sequence[Stack]) -> None:
        self.toolbar.set_stacks(stacks)

    def state(self) -> FilterBrowserState:
        column_visibility = {c.field.name: c.visible for c in self._columns}
        splitter_sizes = tuple(self.splitter.sizes())
        filters = {}
        for data in self._columns:
            if data.filter_widget:
                filters[data.field.name] = data.filter_widget.state()
        state = FilterBrowserState(
            column_visibility=column_visibility,
            splitter_sizes=splitter_sizes,
            filters=filters,
        )
        return state

    def set_state(self, state: FilterBrowserState) -> None:
        for column, data in enumerate(self._columns):
            visible = state.column_visibility.get(data.field.name, True)
            if not visible:
                self.set_column_visible(column, visible)

            filter_state = state.filters.get(data.field.name)
            if data.filter_widget and filter_state:
                data.filter_widget.set_state(filter_state)

        if state.splitter_sizes:
            self.splitter.setSizes(state.splitter_sizes)

    def refresh(self) -> None:
        self.filter_list.refresh()
        super().refresh()

    def toggle_filter_list(self) -> None:
        try:
            collapsed = self.splitter.sizes()[1] == 0
        except IndexError:
            return
        if collapsed:
            size_hint = self.filter_list.minimumSizeHint()
            self.splitter.setSizes((1, size_hint.width()))
        else:
            self.splitter.setSizes((1, 0))

    def _splitter_moved(self) -> None:
        try:
            collapsed = self.splitter.sizes()[1] == 0
        except IndexError:
            return
        if self.filter_button.isChecked() == collapsed:
            self.filter_button.blockSignals(True)
            self.filter_button.setChecked(not collapsed)
            self.filter_button.blockSignals(False)


class BrowserToolbar(QtWidgets.QWidget):
    sort_changed = QtCore.Signal(QtCore.Qt.SortOrder)
    group_changed = QtCore.Signal(Group)
    stack_changed = QtCore.Signal(Stack)
    refreshed = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._groups: tuple[Group, ...] = ()
        self._stacks: tuple[Stack, ...] = ()

        self._init_ui()

    def _init_ui(self) -> None:
        # Layout
        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setContentsMargins(QtCore.QMargins())
        self.setLayout(self._layout)

        # Columns
        self.columns_button = QtWidgets.QPushButton('Columns')
        self.columns_button.setIcon(MaterialIcon('view_column'))
        self.columns_button.setAutoDefault(False)
        self.columns_button.setVisible(False)
        self._layout.addWidget(self.columns_button)

        self.columns_menu = self.columns_button.menu
        self.set_columns_menu = self.columns_button.setMenu

        # Sort
        self.sort_button = QtWidgets.QPushButton('Sort')
        self.sort_button.setIcon(MaterialIcon('sort'))
        self.sort_button.setAutoDefault(False)
        self._layout.addWidget(self.sort_button)

        menu = QtWidgets.QMenu(parent=self.sort_button)
        self.sort_button.setMenu(menu)

        action = QtWidgets.QAction('Ascending', parent=self.sort_button)
        action.setIcon(MaterialIcon('keyboard_arrow_up'))
        func = partial(self.sort_changed.emit, QtCore.Qt.SortOrder.AscendingOrder)
        action.triggered.connect(func)
        menu.addAction(action)
        action = QtWidgets.QAction('Descending', parent=self.sort_button)
        action.setIcon(MaterialIcon('keyboard_arrow_down'))
        func = partial(self.sort_changed.emit, QtCore.Qt.SortOrder.DescendingOrder)
        action.triggered.connect(func)
        menu.addAction(action)

        # Group
        self.groups_button = QtWidgets.QPushButton('Group')
        self.groups_button.setIcon(MaterialIcon('view_agenda'))
        self.groups_button.setAutoDefault(False)
        self.groups_button.setVisible(False)
        self._layout.addWidget(self.groups_button)

        self.groups_menu = RadioMenu(parent=self.groups_button)
        self.groups_menu.selection_changed.connect(self.group_changed)
        self.groups_button.setMenu(self.groups_menu)

        # Stack
        self.stacks_button = QtWidgets.QPushButton('Stack')
        self.stacks_button.setIcon(MaterialIcon('stacks'))
        self.stacks_button.setAutoDefault(False)
        self.stacks_button.setVisible(False)
        self._layout.addWidget(self.stacks_button)

        self.stacks_menu = RadioMenu(parent=self.stacks_button)
        self.stacks_menu.selection_changed.connect(self.stack_changed)
        self.stacks_button.setMenu(self.stacks_menu)

        # Reload
        self._layout.addStretch()

        reload_button = QtWidgets.QPushButton('Reload')
        reload_button.setIcon(MaterialIcon('refresh'))
        reload_button.setAutoDefault(False)
        reload_button.setToolTip('Reload the Browser.')
        reload_button.clicked.connect(self.refreshed)
        self._layout.addWidget(reload_button)

    def group(self) -> Group | None:
        return self.groups_menu.selection()

    def set_group(self, group: Group | None) -> None:
        self.groups_menu.set_selection(group)

    def groups(self) -> tuple[Group, ...]:
        """Return the groups."""

        return self._groups

    def set_groups(self, groups: Sequence[Group]) -> None:
        """Set the groups of a Browser."""

        if not isinstance(groups, tuple):
            groups = tuple(groups)
        self._groups = groups
        self.groups_button.setVisible(bool(groups))

        # Update menu
        items: dict[str, Any] = {'None': None}
        items.update({group.label: group for group in groups})
        self.groups_menu.set_items(items)

    def stack(self) -> Stack | None:
        return self.stacks_menu.selection()

    def set_stack(self, stack: Stack | None) -> None:
        self.stacks_menu.set_selection(stack)

    def stacks(self) -> tuple[Stack, ...]:
        """Return the stacks."""

        return self._stacks

    def set_stacks(self, stacks: Sequence[Stack]) -> None:
        """Set the stacks of a Browser."""

        if not isinstance(stacks, tuple):
            stacks = tuple(stacks)
        self._stacks = stacks
        self.stacks_button.setVisible(bool(stacks))

        # Update menu
        items: dict[str, Any] = {'None': None}
        items.update({stack.label: stack for stack in stacks})
        self.stacks_menu.set_items(items)


class ColumnMenu(SelectionMenu):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self._columns: tuple[ColumnData, ...] = ()

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        self._refresh()
        super().showEvent(event)

    def columns(self) -> tuple[ColumnData, ...]:
        """Return the columns."""

        return self._columns

    def set_columns(self, columns: Sequence[ColumnData]) -> None:
        """
        Set the columns of a Browser.
        These columns should be mutable so they update when visibility changes.
        """

        if not isinstance(columns, tuple):
            columns = tuple(columns)
        self._columns = columns
        self._refresh()

    def _refresh(self) -> None:
        self.clear_items()
        for column, data in enumerate(self._columns):
            if data.enabled:
                label = data.field.label
                self.add_item(label=label, data=data, checked=data.visible)
