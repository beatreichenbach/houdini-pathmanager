from typing import Any

from qt_material_icons import MaterialIcon
from qtpy import QtCore, QtGui, QtWidgets

from pathmanager.core import schema
from pathmanager.widgets.tree import Field, StyledItemDelegate


class PathField(Field):
    def create_item(self, value: schema.Item.Path) -> QtGui.QStandardItem:
        item = super().create_item(value.raw)
        item.setToolTip(value.expanded)
        return item


class PreviewField(Field):
    def create_item(self, value: Any) -> QtGui.QStandardItem:
        item = super().create_item(value)
        item.setIcon(MaterialIcon('warning'))
        item.setToolTip('The action is not supported for parameters with expressions.')
        return item


class HighlightDelegate(StyledItemDelegate):
    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:
        self._draw_highlight(painter, option, index)
        super().paint(painter, option, index)

    def _draw_highlight(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:
        text = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
        highlight = index.data(QtCore.Qt.ItemDataRole.UserRole)
        # highlight = 'text'

        if isinstance(text, str) and isinstance(highlight, str):
            if not text or not highlight or highlight not in text:
                return

            self.initStyleOption(option, index)

            # Do not support WrapText, use QTextDocument if needed.
            wrap_text = option.features & QtWidgets.QStyleOptionViewItem.WrapText
            if wrap_text:
                return

            widget = self.parent()
            if isinstance(widget, QtWidgets.QWidget):
                style = widget.style()
            else:
                style = QtWidgets.QApplication.style()

            # Match the text layout of QCommonStyle.viewItemDrawText
            sub_element = QtWidgets.QStyle.SubElement.SE_ItemViewItemText
            rect = style.subElementRect(sub_element, option, widget)

            pixel_metric = QtWidgets.QStyle.PixelMetric.PM_FocusFrameHMargin
            text_margin = style.pixelMetric(pixel_metric, option, widget) + 1
            adjusted_rect = rect.adjusted(text_margin, 0, -text_margin, 0)

            font_metrics: QtGui.QFontMetrics = option.fontMetrics
            elided_text = font_metrics.elidedText(
                text, QtCore.Qt.TextElideMode.ElideRight, adjusted_rect.width()
            )

            text_rect = font_metrics.boundingRect(elided_text)
            layout_rect = style.alignedRect(
                option.direction,
                option.displayAlignment,
                text_rect.size(),
                adjusted_rect,
            )

            # Get highlighted rect
            start = text.find(highlight)
            end = start + len(highlight)
            left = font_metrics.horizontalAdvance(elided_text, start)
            right = font_metrics.horizontalAdvance(elided_text, end)
            highlight_rect = layout_rect.adjusted(
                left, 0, right - layout_rect.width(), 0
            )

            palette = option.palette
            color = palette.color(QtGui.QPalette.ColorRole.Accent)
            color.setAlphaF(0.5)

            painter.save()
            painter.setBrush(QtGui.QBrush(color))
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setClipRect(option.rect)
            painter.drawRect(highlight_rect)
            painter.restore()


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
