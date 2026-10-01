from __future__ import annotations

from collections.abc import Mapping, Sequence

from qtpy import QtCore, QtGui, QtWidgets

from pathmanager.api import meta
from pathmanager.hosts.houdini import ComboParameter

from ..widgets.filter import MultiFilterWidget
from ..widgets.state import FilterState
from ..widgets.tree import ModelIndex, StyledItemDelegate


class StyledDelegate(StyledItemDelegate):
    use_color: bool = False
    use_icon: bool = True
    items: Sequence = ()

    def createEditor(
        self,
        parent: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: ModelIndex,
    ) -> QtWidgets.QWidget:

        editor = StyledComboParameter(parent=parent)
        editor.set_use_icon(False)

        value = index.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)
        if isinstance(value, meta.IterItem):
            editor.set_items(value.items)
        elif self.items:
            editor.set_items(self.items)

        return editor

    def setEditorData(self, editor: QtWidgets.QWidget, index: ModelIndex) -> None:
        value = index.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)
        if isinstance(editor, StyledComboParameter):
            editor.set_value(value)

    def setModelData(
        self,
        editor: QtWidgets.QWidget,
        model: QtCore.QAbstractItemModel,
        index: ModelIndex,
        value: object = None,
    ) -> None:
        value = editor.value() if isinstance(editor, StyledComboParameter) else value
        super().setModelData(editor, model, index, value)

    def displayText(
        self, value: object, locale: QtCore.QLocale | QtCore.QLocale.Language
    ) -> str:
        if isinstance(value, meta.StyledItem):
            return value.label if value else ''
        return str(value)

    def initStyleOption(
        self, option: QtWidgets.QStyleOptionViewItem, index: ModelIndex
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


class StyledComboParameter(ComboParameter[meta.StyledItem]):
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

    def set_items(
        self,
        items: Mapping[str, meta.StyledItem]
        | Sequence[meta.StyledItem]
        | Sequence[tuple[str, meta.StyledItem]],
    ) -> None:
        if isinstance(items, Mapping):
            values = tuple(items.values())
        else:
            values = tuple(
                value[1] if isinstance(value, tuple) else value for value in items
            )
        self._items = values
        self._update_items()
        self.set_default(values[0] if values else None)

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
            elif self._use_icon and (icon := entity.icon()):
                self.combo.addItem(icon, entity.label, entity)
            else:
                self.combo.addItem(entity.label, entity)

            if self._use_color and isinstance(entity, meta.StyledItem):
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
            v.name for v in (self._filter.value or ()) if isinstance(v, meta.StyledItem)
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

        for checkbox, value in zip(self._checkboxes, self._values, strict=True):
            if isinstance(value, meta.StyledItem):
                checkbox.setText(value.label)
                if self._use_icon and (icon := value.icon()):
                    checkbox.setIcon(icon)
                if self._use_color and value.color():
                    palette = checkbox.palette()
                    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, value.color())
                    self.setPalette(palette)


class HtmlDelegate(StyledItemDelegate):
    """A delegate that draws HTML text. Does not elide text."""

    HtmlRole = QtCore.Qt.ItemDataRole.UserRole

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._document = QtGui.QTextDocument()

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: ModelIndex,
    ) -> None:
        self.initStyleOption(option, index)

        self._document.setHtml(option.text)

        if option.widget:
            style = option.widget.style()
        else:
            style = QtWidgets.QApplication.style()

        if option.state & QtWidgets.QStyle.StateFlag.State_Selected:
            option.text = self._document.toPlainText()
            style.drawControl(
                QtWidgets.QStyle.ControlElement.CE_ItemViewItem, option, painter
            )
            return

        # Draw plain control (background, check marks, icon, focus rect, ...)
        option.text = ''
        style.drawControl(
            QtWidgets.QStyle.ControlElement.CE_ItemViewItem, option, painter
        )

        # Match the text layout of QCommonStyle.viewItemDrawText
        sub_element = QtWidgets.QStyle.SubElement.SE_ItemViewItemText
        rect = style.subElementRect(sub_element, option, option.widget)

        document_size = self._document.size()
        layout_rect = style.alignedRect(
            option.direction,
            option.displayAlignment,
            document_size.toSize(),
            rect,
        )

        # Draw
        painter.save()
        painter.setClipRect(option.rect)
        painter.translate(layout_rect.topLeft())
        self._document.drawContents(painter)
        painter.restore()

    def sizeHint(
        self, option: QtWidgets.QStyleOptionViewItem, index: ModelIndex
    ) -> QtCore.QSize:
        self.initStyleOption(option, index)
        self._document.setHtml(option.text)
        size_hint = self._document.size().toSize()
        size_hint += self._padding
        return size_hint
