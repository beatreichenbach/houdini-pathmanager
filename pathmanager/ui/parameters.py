import logging

from qt_parameters import ParameterWidget
from qtpy import QtCore, QtWidgets

from pathmanager.plugins import PluginManager
from pathmanager.houdini import ComboParameter
from qt_parameters import (
    CollapsibleBox,
    ParameterForm,
)

logger = logging.getLogger(__name__)


class ParametersWidget(QtWidgets.QWidget):
    parameter_changed = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent=parent)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        plugins = PluginManager().get_plugins()

        self.form = ParameterForm('parameters')
        self.form.parameter_changed.connect(self._parameter_changed)

        items = {plugin.label: plugin.name for plugin in plugins}
        parm = ComboParameter('plugin')
        parm.set_label('Mode')
        parm.set_items(items)
        self.form.add_parameter(parm)

        self.forms = {}
        self.boxes = {}
        for plugin in plugins:
            form = plugin.form()
            self.forms[plugin.name] = form

            box = self.form.add_form(form)
            box.set_box_style(CollapsibleBox.Style.SIMPLE)
            box.header.setVisible(False)
            box.setVisible(False)
            self.boxes[plugin.name] = box

        self.boxes[plugins[0].name].setVisible(True)

        layout.addWidget(self.form)

    def _parameter_changed(self, parameter: ParameterWidget) -> None:
        if parameter.name() == 'plugin':
            plugin_name = parameter.value()
            for name, box in self.boxes.items():
                box.setVisible(name == plugin_name)
        self.parameter_changed.emit()

    def values(self) -> dict:
        values = self.form.values()
        return values

    def set_values(self, values: dict) -> None:
        self.form.set_values(values)
