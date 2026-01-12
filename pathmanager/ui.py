import enum

from qt_parameters import (
    BoolParameter,
    EnumParameter,
    IntParameter,
    ParameterForm,
    StringParameter,
)
from qtpy import QtCore, QtWidgets

from pathmanager.browser import FilterBrowser, Group
from pathmanager.filter import BasicFilterWidget, MultiFilterWidget
from pathmanager.hou_qt_parameters import (
    HoudiniEnumParameter,
    HoudiniPathParameter,
    PathParameter,
)
from pathmanager.manager import (
    AnchorMethod,
    ModifyMethod,
    Options,
    ParmType,
    Replace,
    Copy,
    Move,
    Find,
    Version,
    Relative,
)
from pathmanager.tree import Field


class ParameterWidget(QtWidgets.QWidget):
    values_changed = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent=parent)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.forms = {}
        formatter = lambda member: member.value

        # Modify
        parm = HoudiniEnumParameter('method')
        parm.set_enum(ModifyMethod)
        parm.set_formatter(formatter)
        parm.value_changed.connect(self.method_changed)
        layout.addWidget(parm)
        self.modify_parm = parm

        # Replace
        form = ParameterForm('replace')
        self.forms[ModifyMethod.REPLACE] = form

        parm = StringParameter('search')
        form.add_parameter(parm)

        parm = StringParameter('replace')
        form.add_parameter(parm)

        parm = BoolParameter('regex')
        form.add_parameter(parm)

        parm = BoolParameter('match_case')
        form.add_parameter(parm)

        # Copy / Move
        form = ParameterForm('copy')
        self.forms[ModifyMethod.COPY] = form

        parm = HoudiniPathParameter('destination')
        parm.set_method(HoudiniPathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm)

        parm = HoudiniPathParameter('relative_root')
        parm.set_method(HoudiniPathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm, checkable=True)

        # Move
        form = ParameterForm('move')
        self.forms[ModifyMethod.MOVE] = form

        parm = HoudiniPathParameter('destination')
        parm.set_method(HoudiniPathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm)

        parm = HoudiniPathParameter('relative_root')
        parm.set_method(HoudiniPathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm, checkable=True)

        # Find
        form = ParameterForm('find')
        self.forms[ModifyMethod.FIND] = form

        parm = HoudiniPathParameter('root')
        parm.set_method(HoudiniPathParameter.Method.EXISTING_DIR)
        parm.set_default('$HIP')
        form.add_parameter(parm)

        # Version
        form = ParameterForm('version')
        self.forms[ModifyMethod.VERSION] = form

        parm = IntParameter('version')
        parm.set_slider_visible(False)
        parm.set_default(-1)
        form.add_parameter(parm)

        parm = StringParameter('pattern')
        parm.set_default('v(\d+)')
        form.add_parameter(parm)

        # Anchor
        form = ParameterForm('relative')
        self.forms[ModifyMethod.RELATIVE] = form

        parm = HoudiniEnumParameter('anchor')
        parm.set_enum(AnchorMethod)
        parm.set_formatter(formatter)
        form.add_parameter(parm)

        method_parm = parm

        parm = IntParameter('parents')
        parm.set_line_min(0)
        parm.set_slider_visible(False)
        form.add_parameter(parm)

        method_parm.value_changed.connect(
            lambda m, p=parm: p.setEnabled(
                m in (AnchorMethod.RELATIVE_HIP, AnchorMethod.RELATIVE_JOB)
            )
        )

        # Update Minimum Height
        max_size_height = self.sizeHint().height()
        for form in self.forms.values():
            layout.addWidget(form)
            max_size_height = max(max_size_height, self.sizeHint().height())
            form.setContentsMargins(QtCore.QMargins())
            form.setVisible(False)
            form.parameter_changed.connect(self.values_changed)

        self.setMinimumHeight(max_size_height)

        self.method_changed(ModifyMethod.REPLACE)

    def method_changed(self, method: ModifyMethod) -> None:
        for m, form in self.forms.items():
            form.setVisible(m == method)
        self.values_changed.emit()

    def values(self) -> Options:
        values = Options(
            method=self.modify_parm.value(),
            replace=Replace(**self.forms[ModifyMethod.REPLACE].values()),
            copy=Copy(**self.forms[ModifyMethod.COPY].values()),
            move=Move(**self.forms[ModifyMethod.MOVE].values()),
            find=Find(**self.forms[ModifyMethod.FIND].values()),
            version=Version(**self.forms[ModifyMethod.VERSION].values()),
            relative=Relative(**self.forms[ModifyMethod.RELATIVE].values()),
        )
        return values


class PathManager(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

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

        self.browser.add_column(field=Field('preview', editable=True))

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
        button_layout.addWidget(progress_bar)

        button_layout.addStretch()

        label = QtWidgets.QLabel('Live Preview')
        button_layout.addWidget(label)
        parm = QtWidgets.QCheckBox()
        button_layout.addWidget(parm)

        button = QtWidgets.QPushButton('Preview')
        button_layout.addWidget(button)

        button = QtWidgets.QPushButton('Commit')
        button_layout.addWidget(button)

        layout.addLayout(button_layout)

        layout.setStretch(0, 1)

        from pathmanager.manager import Manager

        self.manager = Manager()
        self.items = self.manager.get_items()
        self.browser.add_elements(self.items)
        self.parameter_widget.values_changed.connect(self.update_items)

    def update_items(self) -> None:
        self.manager.update_previews(self.items, self.parameter_widget.values())
        self.browser.clear()
        self.browser.add_elements(self.items)
