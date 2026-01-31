from __future__ import annotations

import dataclasses
import enum
import logging
import operator
from collections.abc import Container
from typing import Any, Callable, Optional, Sequence

from qt_material_icons import MaterialIcon
from qt_parameters import (
    BoolParameter,
    CollapsibleBox,
    FloatParameter,
    IntParameter,
    StringParameter,
)
from qt_parameters.scrollarea import VerticalScrollArea
from qtpy import QtCore, QtGui, QtWidgets

ColorGroup = QtGui.QPalette.ColorGroup
ColorRole = QtGui.QPalette.ColorRole

logger = logging.getLogger(__name__)


def is_in(a: Any, b: Container) -> bool:
    return a in b


def is_not_in(a: Any, b: Container) -> bool:
    return a not in b


class Filter:
    value: Any = None
    match: Optional[Callable] = operator.eq
    role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole
    inverted: bool = False

    def __repr__(self) -> str:
        match = self.match.__name__ if self.match else None
        return (
            f'{self.__class__.__name__}'
            f'(value={self.value!r}, '
            f'match={match!r}, '
            f'role={self.role})'
        )

    def accepts(self, value: Any) -> bool:
        if self.match is None or value is None:
            return True

        # Note: Allow values like 0 but not other falsy values.
        if self.value == 0:
            pass
        elif not self.value:
            return True
        return self.match(value, self.value) != self.inverted


@dataclasses.dataclass
class FilterState:
    value: Any = None
    inverted: bool = False
    match: Any = None


class FilterWidget(CollapsibleBox):
    filter_changed = QtCore.Signal(Filter)

    def __init__(
        self, title: str = '', parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(title, parent)

        self._filter = Filter()
        self._default: Any = None

    def _init_ui(self) -> None:
        super()._init_ui()

        self.set_box_style(CollapsibleBox.Style.BUTTON)
        self.set_collapsible(True)
        self.set_collapsed(True)
        self.setLayout(QtWidgets.QVBoxLayout())

        header_layout = self.header.layout()
        header_layout.setSpacing(0)

        invert_icon = MaterialIcon('block')
        palette = QtWidgets.QApplication.palette()
        color = palette.color(ColorGroup.Normal, ColorRole.WindowText)
        invert_icon.set_color(color, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
        color = palette.color(ColorGroup.Disabled, ColorRole.WindowText)
        invert_icon.set_color(color, QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)

        self.invert_button = QtWidgets.QToolButton()
        self.invert_button.setIcon(invert_icon)
        self.invert_button.setAutoRaise(True)
        self.invert_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.invert_button.setCheckable(True)
        self.invert_button.toggled.connect(self.set_inverted)
        header_layout.insertWidget(header_layout.count() - 1, self.invert_button)

        self.reset_button = QtWidgets.QToolButton()
        self.reset_button.setIcon(MaterialIcon('undo'))
        self.reset_button.setAutoRaise(True)
        self.reset_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.reset_button.setEnabled(False)
        self.reset_button.clicked.connect(self.reset)
        header_layout.insertWidget(header_layout.count() - 1, self.reset_button)

    def filter(self) -> Filter:
        return self._filter

    def set_filter(self, value: Filter) -> None:
        self._filter = value
        self.filter_changed.emit(self._filter)

    def inverted(self) -> bool:
        return self._filter.inverted

    def set_inverted(self, inverted: bool) -> None:
        if self._filter.inverted == inverted:
            return

        self.invert_button.blockSignals(True)
        self.invert_button.setChecked(inverted)
        self.invert_button.blockSignals(False)

        self._filter.inverted = inverted
        self.filter_changed.emit(self._filter)

    def default(self) -> Any:
        return self._default

    def set_default(self, value: Any) -> None:
        self._default = value
        self.set_value(value)

    def value(self) -> Any:
        return self._filter.value

    def set_value(self, value: Any) -> None:
        if self._filter.value != value:
            self._filter.value = value
            self.filter_changed.emit(self._filter)
            self._refresh()

    def state(self) -> FilterState:
        state = FilterState(
            value=self._filter.value,
            inverted=self._filter.inverted,
        )
        return state

    def set_state(self, state: FilterState) -> None:
        if state.value is None:
            self.reset()
        else:
            self.set_value(state.value)
            self.set_inverted(state.inverted)

        # In case the state value matches the default, compare the actual value.
        self.set_collapsed(self._filter.value == self._default)

    def reset(self) -> None:
        self.set_value(self._default)
        self.set_inverted(False)

    def _clear_layout(self) -> None:
        while item := self.layout().takeAt(0):
            if widget := item.widget():
                widget.deleteLater()

    def _refresh(self) -> None:
        has_changes = self._filter.value != self._default
        if has_changes:
            weight = QtGui.QFont.Weight.Bold
        else:
            weight = QtGui.QFont.Weight.Normal
        font = self.title_label.font()
        font.setWeight(weight)
        self.title_label.setFont(font)

        self.reset_button.setEnabled(has_changes)


class MultiFilterWidget(FilterWidget):
    def __init__(
        self, title: str = '', parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(title, parent)

        self._filter.value = set()
        self._filter.match = is_in
        self._default = set()
        self._values = ()
        self._checkboxes: tuple[QtWidgets.QCheckBox, ...] = ()

    def set_value(self, value: Sequence) -> None:
        """Set the value, if the value doesn't exist, add it."""

        value = set(value)
        if not value.issubset(self._values):
            values = (*self._values, *value)
            self.set_values(values)

        if self._filter.value != value:
            self._filter.value = value
            self.filter_changed.emit(self._filter)
            self._refresh()

        # Update checkboxes requires self._filter.value to be set.
        self._refresh_checkboxes()

    def values(self) -> tuple:
        return tuple(self._values)

    def set_values(self, values: Sequence) -> None:
        """
        Set the available values.
        This filters None values, sorts and ensures unique values.
        """

        values = tuple(sorted(set(v for v in values if v is not None)))
        if self._values != values:
            self._values = values
            self._update_checkboxes()
            self._refresh_checkboxes()

    def _checkbox_toggled(self) -> None:
        values = []
        for checkbox, value in zip(self._checkboxes, self._values):
            if checkbox.isChecked():
                values.append(value)
        super().set_value(set(values))

    def _update_checkboxes(self) -> None:
        """Rebuild the checkboxes to match all values."""

        self._clear_layout()
        checkboxes = []
        for value in self._values:
            checkbox = QtWidgets.QCheckBox()
            checkbox.setText(str(value))
            checkbox.toggled.connect(self._checkbox_toggled)
            checkboxes.append(checkbox)
            self.layout().addWidget(checkbox)
        self._checkboxes = tuple(checkboxes)

    def _refresh_checkboxes(self) -> None:
        """Refresh the checked status on the checkboxes."""

        for checkbox, value in zip(self._checkboxes, self._values):
            checkbox.blockSignals(True)
            checkbox.setChecked(value in self._filter.value)
            checkbox.blockSignals(False)


class DateFilterWidget(FilterWidget):
    class Limit(enum.Enum):
        ANY = None
        BEFORE = operator.lt
        AFTER = operator.gt

    def __init__(self, name: str = '', parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(name, parent)

        self._default: QtCore.QDateTime = QtCore.QDateTime.currentDateTime()
        self._filter.value = self._default
        self._filter.match = None

        self.format = self.datetime_edit.displayFormat
        self.set_format = self.datetime_edit.setDisplayFormat

    def _init_ui(self) -> None:
        super()._init_ui()

        self.limit_combo = QtWidgets.QComboBox()
        self.limit_combo.addItem('Any', DateFilterWidget.Limit.ANY)
        self.limit_combo.addItem('Before', DateFilterWidget.Limit.BEFORE)
        self.limit_combo.addItem('After', DateFilterWidget.Limit.AFTER)
        self.limit_combo.currentIndexChanged.connect(self._values_changed)
        self.layout().addWidget(self.limit_combo)

        self.datetime_edit = QtWidgets.QDateTimeEdit()
        self.datetime_edit.setEnabled(False)
        self.datetime_edit.dateTimeChanged.connect(self._values_changed)
        self.layout().addWidget(self.datetime_edit)

    def value(self) -> QtCore.QDateTime:
        return super().value()

    def set_value(self, value: QtCore.QDateTime) -> None:
        super().set_value(value)

        self.datetime_edit.blockSignals(True)
        self.datetime_edit.setDateTime(value)
        self.datetime_edit.blockSignals(False)

    def limit(self) -> Limit:
        return self.limit_combo.currentData(QtCore.Qt.ItemDataRole.UserRole)

    def set_limit(self, limit: Limit) -> None:
        index = self.limit_combo.findData(limit, QtCore.Qt.ItemDataRole.UserRole)
        if index >= 0:
            self.limit_combo.setCurrentIndex(index)

    def state(self) -> FilterState:
        limit = self.limit()
        if limit == DateFilterWidget.Limit.ANY:
            value = None
        else:
            value = self.value().toString(QtCore.Qt.DateFormat.ISODate)
        state = FilterState(
            value=value,
            inverted=self._filter.inverted,
            match=limit.name,
        )
        return state

    def set_state(self, state: FilterState) -> None:
        if state.value:
            value = QtCore.QDateTime.fromString(
                state.value, QtCore.Qt.DateFormat.ISODate
            )
            self.set_value(value)
            self.set_inverted(state.inverted)
            try:
                limit = DateFilterWidget.Limit[state.match]
            except KeyError:
                limit = None
            self.set_limit(limit)
            self.set_collapsed(False)
        else:
            self.reset()
            self.set_collapsed(True)

    def reset(self) -> None:
        self.set_limit(DateFilterWidget.Limit.ANY)
        super().reset()

    def _values_changed(self) -> None:
        """Handle the change of the DateTimeEdit or the Limit ComboBox values."""

        value = self.datetime_edit.dateTime()
        limit = self.limit_combo.currentData(QtCore.Qt.ItemDataRole.UserRole)
        match = limit.value
        if limit == DateFilterWidget.Limit.ANY:
            value = self._default

        if self._filter.value != value or self._filter.match != match:
            self._filter.value = value
            self._filter.match = match
            self.filter_changed.emit(self._filter)
            self._refresh()
            if match is not None:
                # Manually enable the reset button because `match` is not tracked.
                self.reset_button.setEnabled(True)

        self.datetime_edit.setEnabled(match is not None)


class BasicFilterWidget(FilterWidget):
    BasicType = float | int | str | bool

    def __init__(
        self,
        title: str = '',
        parent: QtWidgets.QWidget | None = None,
        cls: type[BasicType] = str,
    ) -> None:
        super().__init__(title, parent)
        self._update_parm(cls)

    def value(self) -> BasicType:
        return super().value()

    def set_value(self, value: BasicType) -> None:
        super().set_value(value)

        self.parm.blockSignals(True)
        self.parm.set_value(value)
        self.parm.blockSignals(False)

    def default(self) -> BasicType:
        return super().default()

    def set_default(self, value: BasicType) -> None:
        super().set_default(value)

    def _update_parm(self, cls: type[BasicType]) -> None:
        self._clear_layout()

        if issubclass(cls, float):
            self.parm = FloatParameter()
        elif issubclass(cls, int):
            self.parm = IntParameter()
        elif issubclass(cls, str):
            self.parm = StringParameter()
            self._filter.match = operator.contains
        elif issubclass(cls, bool):
            self.parm = BoolParameter()

        if isinstance(self._default, cls):
            self.parm.set_default(self._default)
        else:
            self._default = self.parm.default()

        self.parm.value_changed.connect(super().set_value)
        self.layout().addWidget(self.parm)


class FilterListWidget(VerticalScrollArea):
    filter_changed = QtCore.Signal(Filter)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._model: QtGui.QStandardItemModel | None = None
        self._widgets: dict[int, FilterWidget] = {}

        self._init_ui()

    def _init_ui(self) -> None:
        widget = QtWidgets.QWidget()
        self.setWidget(widget)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.addStretch()
        widget.setLayout(self._layout)

    def minimumSizeHint(self) -> QtCore.QSize:
        size_hint = super().minimumSizeHint()
        size_hint.setWidth(max(size_hint.width(), 256))
        return size_hint

    def add_filter_widget(self, column: int, widget: FilterWidget) -> None:
        index = self._layout.count() - 1
        self._layout.insertWidget(index, widget)
        widget.filter_changed.connect(self.filter_changed.emit)
        self._widgets[column] = widget
        self.refresh_column(column)

    def remove_filter_widget(
        self, column: int = -1, widget: FilterWidget | None = None
    ) -> None:
        """Remove a FilterWidget. Either provide a column or a widget."""

        if column < 0:
            for c, w in self._widgets.items():
                if w == widget:
                    column = c
                    break
        widget = self._widgets.get(column)
        if widget:
            self._layout.removeWidget(widget)
            widget.deleteLater()

    def filter_widgets(self) -> tuple[FilterWidget, ...]:
        return tuple(self._widgets.values())  # noqa

    def filters(self) -> dict[int, Filter]:
        return {column: widget.filter() for column, widget in self._widgets.items()}

    def model(self) -> QtGui.QStandardItemModel:
        return self._model

    def set_model(self, model: QtGui.QStandardItemModel) -> None:
        self._model = model
        self.refresh()

    def refresh(self) -> None:
        for column, widget in self._widgets.items():
            self.refresh_column(column)

    def refresh_column(self, column: int) -> None:
        """
        Refresh the FilterWidget for a column.
        If the model has updated, this is used to rebuild the values in
        MultiFilterWidgets.
        """
        widget = self._widgets.get(column)
        if not widget or not self._model:
            return

        enabled = column < self._model.columnCount()
        if enabled and isinstance(widget, MultiFilterWidget):
            value = widget.value()
            role = widget.filter().role
            values = self._get_column_values(column, role)
            widget.set_values(values)

            # After setting the new values, restore the original state.
            widget.set_value(value)

        widget.setEnabled(enabled)
        widget.setVisible(enabled)

    def _get_column_values(
        self,
        column: int,
        role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole,
        parent: QtCore.QModelIndex | None = None,
    ) -> tuple:
        """Return all values of a column for a given role recursively."""

        values = set()
        if parent is None:
            parent = QtCore.QModelIndex()

        for row in range(self._model.rowCount(parent)):
            index = self._model.index(row, column, parent)
            value = index.data(role)
            values.add(value)
            sibling_index = index.siblingAtColumn(0)
            values.update(self._get_column_values(column, role, sibling_index))
        return tuple(values)
