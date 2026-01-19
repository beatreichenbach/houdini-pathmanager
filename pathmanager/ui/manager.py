import logging
from functools import partial

from qtpy import QtCore, QtWidgets

from pathmanager.core import Host
from pathmanager.plugins import PluginManager
from pathmanager.tree import StyledDelegate, StyledFilterWidget
from pathmanager.widgets import (
    BasicFilterWidget,
    CheckBoxButton,
    Field,
    FilterBrowser,
    Group,
    Stack,
)
from .parameters import ParametersWidget
from .tree import PathField, PreviewField

logger = logging.getLogger(__name__)


class PathManager(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._host: Host | None = None
        self._items = None

        self._init_ui()

    def _init_ui(self) -> None:
        self.resize(QtCore.QSize(1280, 720))

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Browser
        self.browser = FilterBrowser()
        self.browser.search_line.setVisible(False)
        self.browser.model_expired.connect(self._load_items)
        layout.addWidget(self.browser)

        self.browser.add_column(
            field=Field('parm_name'),
            filter_widget=BasicFilterWidget('Parm Name', cls=str),
        )

        self.browser.add_column(
            field=Field('parm_type'),
            filter_widget=StyledFilterWidget('Parm Type'),
            delegate=StyledDelegate(),
        )

        self.browser.add_column(
            field=Field('node_path'),
            filter_widget=BasicFilterWidget('Node Path', cls=str),
        )

        self.browser.add_column(
            field=Field('node_type.category', label='Node Category'),
            filter_widget=BasicFilterWidget('Node Type Category', cls=str),
        )

        self.browser.add_column(
            field=Field('node_type.name', label='Node Type'),
            filter_widget=BasicFilterWidget('Node Type Name', cls=str),
        )

        self.browser.add_column(
            field=Field('status'),
            filter_widget=StyledFilterWidget('Status'),
            delegate=StyledDelegate(),
        )

        self.browser.add_column(
            field=PathField('path'), filter_widget=BasicFilterWidget('Path', cls=str)
        )

        self.browser.add_column(field=PreviewField('preview'))

        for widget in self.browser.filter_list.filter_widgets():
            widget.set_collapsed(False)

        # Toolbar
        stacks = (Stack(name='path'),)
        self.browser.set_stacks(stacks)

        groups = (Group(name='node_path'),)
        self.browser.set_groups(groups)

        toolbar_layout = self.browser.toolbar.layout()
        self.selection_button = CheckBoxButton('Selection')
        toolbar_layout.insertWidget(5, self.selection_button)

        # Parameters
        self.parameters_widget = ParametersWidget()
        self.parameters_widget.parameter_changed.connect(self._values_changed)
        layout.addWidget(self.parameters_widget)

        # Button Layout
        button_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(button_layout)

        self.status_bar = QtWidgets.QStatusBar()
        button_layout.addWidget(self.status_bar)

        progress_bar = QtWidgets.QProgressBar()
        progress_bar.setVisible(False)
        button_layout.addWidget(progress_bar)

        self.preview_button = CheckBoxButton('Preview')
        self.preview_button.setChecked(True)
        self.preview_button.toggled.connect(self._values_changed)
        button_layout.addWidget(self.preview_button)

        button = QtWidgets.QPushButton('Commit Selected')
        button.clicked.connect(partial(self._commit_items, True))
        button_layout.addWidget(button)

        button = QtWidgets.QPushButton('Commit')
        button.clicked.connect(self._commit_items)
        button_layout.addWidget(button)

        button_layout.setStretch(0, 1)

        # Global
        layout.setStretch(0, 1)

    def set_host(self, host: Host) -> None:
        self._host = host
        self._load_items()

    def reload(self) -> None:
        self._load_items()

    def _values_changed(self) -> None:
        if self.preview_button.isChecked():
            self._preview_items()

    def _load_items(self) -> None:
        self.browser.clear()
        if not self._host:
            return

        selected = self.selection_button.isChecked()
        items = self._host.get_items(selected=selected)
        self.browser.add_elements(items)

        self._preview_items()

    def _refresh_items(self) -> None:
        self.browser.model.refresh_column(7)

    def _preview_items(self) -> None:
        values = self.parameters_widget.values()
        plugin_name = values['plugin']
        plugin = PluginManager().get(plugin_name)

        items = self.browser.elements()
        plugin.preview(items, values)
        self._refresh_items()

    def _commit_items(self, selected: bool = False) -> None:
        values = self.parameters_widget.values()
        plugin_name = values['plugin']
        plugin = PluginManager().get(plugin_name)

        if selected:
            items = self.browser.selected_elements()
        else:
            items = self.browser.visible_elements()

        plugin.process(items, values)
        self._host.update_items(items)
        self._load_items()
