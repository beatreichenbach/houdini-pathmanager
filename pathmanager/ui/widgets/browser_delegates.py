from __future__ import annotations

from qtpy import QtCore, QtGui, QtWidgets

from .browser_fields import ModelIndex

StateFlag = QtWidgets.QStyle.StateFlag


class StyledItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._padding = QtCore.QSize(0, 4)

    def sizeHint(
        self, option: QtWidgets.QStyleOptionViewItem, index: ModelIndex
    ) -> QtCore.QSize:
        size_hint = super().sizeHint(option, index)
        size_hint += self._padding
        return size_hint

    def setModelData(
        self,
        editor: QtWidgets.QWidget,
        model: QtCore.QAbstractItemModel,
        index: ModelIndex,
        value: object = None,
    ) -> None:
        """Set data on all selected rows."""

        # Include the current index, in case it is not selected.
        indexes = {index}
        parent = self.parent()
        if isinstance(parent, QtWidgets.QTreeView):
            selection_model = parent.selectionModel()
            indexes.update(selection_model.selectedRows(index.column()))

        for i in indexes:
            if value is None:
                super().setModelData(editor, model, i)
            else:
                model.setData(i, value, QtCore.Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(
        self,
        editor: QtWidgets.QWidget,
        option: QtWidgets.QStyleOption,
        index: ModelIndex,
    ) -> None:
        editor.setGeometry(option.rect)

    def padding(self) -> QtCore.QSize:
        return self._padding

    def set_padding(self, padding: QtCore.QSize) -> None:
        self._padding = padding


class ImageDelegate(QtWidgets.QStyledItemDelegate):
    """Delegate to display image thumbnails."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._aspect_ratio = 16 / 9
        self._max_width = 192
        self._width = 64
        self._size = self._get_size()

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: ModelIndex,
    ) -> None:
        widget = self.parent()
        if not isinstance(widget, QtWidgets.QWidget):
            return

        style = widget.style()
        self.initStyleOption(option, index)
        painter.save()
        painter.setClipRect(option.rect)

        # Panel
        style.drawPrimitive(
            QtWidgets.QStyle.PrimitiveElement.PE_PanelItemViewItem,
            option,
            painter,
            widget,
        )

        # Pixmap
        pixmap_rect = QtCore.QRect(option.rect)
        pixmap_rect.setSize(self._size)
        mode = QtGui.QIcon.Mode.Normal
        if not option.state & StateFlag.State_Enabled:
            mode = QtGui.QIcon.Mode.Disabled
        elif option.state & StateFlag.State_Selected:
            mode = QtGui.QIcon.Mode.Selected

        if option.state & StateFlag.State_Open == StateFlag.State_Open:
            state = QtGui.QIcon.State.On
        else:
            state = QtGui.QIcon.State.Off
        option.icon.paint(painter, pixmap_rect, option.decorationAlignment, mode, state)

        # Focus Rect
        if option.state & StateFlag.State_HasFocus:
            option_focus = QtWidgets.QStyleOptionFocusRect()
            option_focus.rect = option.rect
            option_focus.state = option.state
            option_focus.state |= StateFlag.State_KeyboardFocusChange
            option_focus.state |= StateFlag.State_Item

            if option.state & StateFlag.State_Enabled:
                color_group = QtGui.QPalette.ColorGroup.Normal
            else:
                color_group = QtGui.QPalette.ColorGroup.Disabled

            if option.state & StateFlag.State_Selected:
                role = QtGui.QPalette.ColorRole.Highlight
            else:
                role = QtGui.QPalette.ColorRole.Window
            option_focus.backgroundColor = option.palette.color(color_group, role)
            style.drawPrimitive(
                QtWidgets.QStyle.PrimitiveElement.PE_FrameFocusRect,
                option_focus,
                painter,
                widget,
            )

        painter.restore()

    def sizeHint(
        self, option: QtWidgets.QStyleOptionViewItem, index: ModelIndex
    ) -> QtCore.QSize:
        return self._size

    def aspect_ratio(self) -> float:
        return self._aspect_ratio

    def set_aspect_ratio(self, aspect_ratio: float) -> None:
        self._aspect_ratio = aspect_ratio
        self._size = self._get_size()

    def max_width(self) -> int:
        return self._max_width

    def set_max_width(self, max_width: int) -> None:
        self._max_width = max_width
        self._size = self._get_size()

    def width(self) -> int:
        return self._width

    def set_width(self, width: int) -> None:
        self._width = min(width, self._max_width)
        self._size = self._get_size()

    def _get_size(self) -> QtCore.QSize:
        return QtCore.QSize(self._width, int(self._width / self._aspect_ratio))


class DateDelegate(StyledItemDelegate):
    def displayText(
        self, value: object, locale: QtCore.QLocale | QtCore.QLocale.Language
    ) -> str:
        if isinstance(value, QtCore.QDateTime):
            return value.toLocalTime().toString()
        return ''
