from __future__ import annotations

import dataclasses
import enum

import qt_parameters
from qt_parameters import (
    BoolParameter,
    EnumParameter,
    IntParameter,
    ParameterEditor,
    ParameterForm,
    StringParameter,
)
from qtpy import QtCore, QtWidgets

import tests
from pathmanager.tree import Field
from tests import application
from pathmanager.browser import Browser, Group


class ModifyMethod(enum.Enum):
    NONE = 'None'
    REPLACE = 'Replace'
    COPY = 'Copy'
    MOVE = 'Move'
    SEARCH = 'Search'
    VERSION = 'Version'


class AnchorMethod(enum.Enum):
    NONE = 'None'
    RELATIVE_HIP = 'Relative to $HIP'
    RELATIVE_JOB = 'Relative to $JOB'
    ABSOLUTE = 'Absolute'


class ParmType(enum.Enum):
    FILE = 'File'
    IMAGE = 'File - Image'
    GEOMETRY = 'File - Geometry'
    DIRECTORY = 'File - Directory'


def main() -> None:
    with application():
        editor = ParameterEditor()

        # Filter
        form = ParameterForm('filter')
        parm = StringParameter('node_path')
        form.add_parameter(parm)

        parm = StringParameter('node_type')
        form.add_parameter(parm)

        parm = StringParameter('parm_name')
        form.add_parameter(parm)

        parm = StringParameter('parm_type')
        form.add_parameter(parm)

        parm = StringParameter('path')
        form.add_parameter(parm)

        parm = BoolParameter('show_empty')
        parm.set_label('Show Empty Parameters')
        form.add_parameter(parm)

        parm = BoolParameter('show_missing_only')
        parm.set_label('Show Missing Only')
        form.add_parameter(parm)

        editor.add_form(form)

        formatter = lambda member: member.value

        # Button
        layout = QtWidgets.QHBoxLayout()

        layout.addStretch()

        button = QtWidgets.QPushButton('Reload')
        layout.addWidget(button)

        editor.add_layout(layout)

        # Modify
        form = editor
        parm = EnumParameter('method')
        parm.set_enum(ModifyMethod)
        parm.set_formatter(formatter)
        form.add_parameter(parm)

        # Replace
        form = ParameterForm(name='replace')

        parm = StringParameter('from')
        form.add_parameter(parm)

        parm = StringParameter('to')
        form.add_parameter(parm)

        parm = BoolParameter('regex')
        form.add_parameter(parm)

        parm = BoolParameter('match_case')
        form.add_parameter(parm)
        editor.add_form(form)

        # Copy
        form = ParameterForm(name='copy')
        parm = StringParameter('destination')
        form.add_parameter(parm)

        parm = StringParameter('relative_root')
        form.add_parameter(parm, checkable=True)
        editor.add_form(form)

        form = ParameterForm(name='move')
        parm = StringParameter('destination')
        form.add_parameter(parm)

        parm = StringParameter('relative_root')
        form.add_parameter(parm, checkable=True)
        editor.add_form(form)

        form = ParameterForm(name='search')
        parm = StringParameter('root')
        parm.set_default('$HIP')
        form.add_parameter(parm)
        editor.add_form(form)

        form = ParameterForm(name='version')
        parm = IntParameter('version')
        parm.set_slider_visible(False)
        parm.set_default(-1)
        form.add_parameter(parm)

        parm = StringParameter('version_pattern')
        parm.set_default('v(\d+)')
        form.add_parameter(parm)
        editor.add_form(form)

        # Anchor
        form = ParameterForm(name='anchor')

        parm = EnumParameter('method')
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

        editor.add_form(form)

        editor.show()

        # Button Layout
        layout = QtWidgets.QHBoxLayout()

        layout.addStretch()

        label = QtWidgets.QLabel('Live Preview')
        layout.addWidget(label)
        parm = QtWidgets.QCheckBox()
        layout.addWidget(parm)

        button = QtWidgets.QPushButton('Preview')
        layout.addWidget(button)

        button = QtWidgets.QPushButton('Commit')
        layout.addWidget(button)

        editor.add_layout(layout)


if __name__ == '__main__':
    tests.init()
    main()
