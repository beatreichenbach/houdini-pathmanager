from qtpy import QtCore, QtGui, QtWidgets

from pathmanager import schema
from pathmanager.widgets.tree import Field, StyledItemDelegate

ItemDataRole = QtCore.Qt.ItemDataRole


class PathField(Field):
    def create_item(self, value: schema.Item.Path) -> QtGui.QStandardItem:
        text = value.raw if value is not None else ''
        tooltip = value.expanded if value is not None else ''
        item = super().create_item(text)
        item.setToolTip(tooltip)
        return item

    def refresh(self, value: schema.Item.Path, index: QtCore.QModelIndex) -> None:
        text = value.raw if value is not None else ''
        tooltip = value.expanded if value is not None else ''
        super().refresh(text, index)
        index.model().setData(index, tooltip, ItemDataRole.ToolTipRole)


class PreviewField(Field):
    def create_item(self, value: schema.Item.Preview) -> QtGui.QStandardItem:
        text = value.raw if value is not None else ''
        item = super().create_item(text)
        return item

    def refresh(self, value: schema.Item.Preview, index: QtCore.QModelIndex) -> None:
        text = value.raw if value is not None else ''
        super().refresh(text, index)


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
        index: QtCore.QModelIndex,
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
        self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex
    ) -> QtCore.QSize:
        self.initStyleOption(option, index)
        self._document.setHtml(option.text)
        size_hint = self._document.size().toSize()
        size_hint += self._padding
        return size_hint
