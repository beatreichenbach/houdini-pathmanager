import difflib
import logging
from typing import Any

from qt_parameters import ComboParameter
from qtpy import QtCore, QtGui, QtWidgets

from pathmanager import schema
from pathmanager.hosts import base
from pathmanager.plugins.replace import ReplacePlugin
from pathmanager.widgets.browser import FilterBrowser, Group
from pathmanager.widgets.button import CheckBoxButton
from pathmanager.widgets.filter import BasicFilterWidget, MultiFilterWidget
from pathmanager.widgets.tree import Field, StyledItemDelegate

logger = logging.getLogger(__name__)


class ParameterWidget(QtWidgets.QWidget):
    values_changed = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self.plugins = (ReplacePlugin(),)
        self.forms = {}

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        items = {plugin.label: plugin.name for plugin in self.plugins}
        self.plugin_parm = ComboParameter('plugin')
        self.plugin_parm.set_items(items)
        self.plugin_parm.value_changed.connect(self.plugin_changed)
        layout.addWidget(self.plugin_parm)

        max_size_height = self.sizeHint().height()

        for plugin in self.plugins:
            form = plugin.form()
            form.parameter_changed.connect(self.values_changed)
            self.forms[plugin.name] = form

            layout.addWidget(form)
            form.setContentsMargins(QtCore.QMargins())

            max_size_height = max(max_size_height, self.sizeHint().height())
            form.setVisible(False)

        self.setMinimumHeight(max_size_height)

        self.plugin_changed(self.plugins[0].name)

    def plugin_changed(self, selection: str) -> None:
        for name, form in self.forms.items():
            form.setVisible(name == selection)
        self.values_changed.emit()

    def values(self) -> dict:
        name = self.plugin_parm.value()
        plugin = self.plugins[0]
        form = self.forms[name]
        values = {'plugin': plugin, 'values': form.values()}
        return values


# class HtmlField(Field):
#     def create_item(self, value: Any) -> QtGui.QStandardItem:


class PathManager(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._host = None
        self._items = None

        self._init_ui()

    def _init_ui(self) -> None:
        self.resize(QtCore.QSize(1280, 720))

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Browser
        self.browser = FilterBrowser()
        self.browser.search_line.setVisible(False)

        filter_widget = BasicFilterWidget('Name', cls=str)
        self.browser.add_column(field=Field('name'), filter_widget=filter_widget)

        filter_widget = MultiFilterWidget('Parm Type')
        self.browser.add_column(field=Field('parm_type'), filter_widget=filter_widget)

        filter_widget = BasicFilterWidget('Node', cls=str)
        self.browser.add_column(field=Field('node_path'), filter_widget=filter_widget)

        filter_widget = MultiFilterWidget('Status')
        self.browser.add_column(field=Field('status'), filter_widget=filter_widget)

        filter_widget = BasicFilterWidget('Path', cls=str)
        self.browser.add_column(field=Field('path'), filter_widget=filter_widget)

        delegate = HtmlDelegate()
        delegate.set_padding(QtCore.QSize(0, 16))
        self.browser.add_column(field=Field('preview'), delegate=delegate)

        for widget in self.browser.filter_list.filter_widgets():
            widget.set_collapsed(False)

        self.browser.toggle_filter_list()

        groups = (
            Group(name='node_path'),
            Group(name='path'),
        )
        self.browser.set_groups(groups)

        layout.addWidget(self.browser)

        # Parameters
        self.parameter_widget = ParameterWidget()
        layout.addWidget(self.parameter_widget)

        # Button Layout
        button_layout = QtWidgets.QHBoxLayout()

        progress_bar = QtWidgets.QProgressBar()
        progress_bar.setVisible(False)
        button_layout.addWidget(progress_bar)

        button_layout.addStretch()

        self.preview_button = CheckBoxButton('Preview')
        self.preview_button.setChecked(True)
        self.preview_button.toggled.connect(self._values_changed)
        button_layout.addWidget(self.preview_button)

        button = QtWidgets.QPushButton('Commit')
        button.clicked.connect(self.commit)
        button_layout.addWidget(button)

        layout.addLayout(button_layout)

        layout.setStretch(0, 1)

    def set_host(self, host: base.Host) -> None:
        self._host = host
        self._items = self._host.get_items()
        self.browser.add_elements(self._items)
        self.parameter_widget.values_changed.connect(self._values_changed)

    def update_items(self) -> None:
        values = self.parameter_widget.values()
        plugin = values['plugin']
        plugin.preview(self._items, values['values'])

        self.browser.clear()
        self.browser.add_elements(self._items)

    def commit(self) -> None:
        values = self.parameter_widget.values()
        plugin = values['plugin']
        plugin.process(self._items, values['values'])

        self.browser.clear()
        self.browser.add_elements(self._items)

    def _values_changed(self) -> None:
        if not self.preview_button.isChecked():
            return
        self.update_items()


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
