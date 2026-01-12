import logging

from qt_parameters import CollapsibleBox, ParameterForm
from qtpy import QtWidgets

from pathmanager.houdini import ComboParameter
from pathmanager.plugins import PluginManager

logger = logging.getLogger(__name__)


class Parameters(ParameterForm):
    def __init__(self, name: str = '', parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(name=name, parent=parent)

        plugins = PluginManager().get_plugins()
        items = {plugin.label: plugin.name for plugin in plugins}

        parm = ComboParameter('plugin')
        parm.set_label('Mode')
        parm.set_items(items)
        parm.value_changed.connect(self._plugin_changed)
        self.add_parameter(parm)

        self.forms = {}
        self.boxes = {}

        max_height = self.minimumSizeHint().height()
        for plugin in plugins:
            form = plugin.form()
            self.forms[plugin.name] = form

            box = self.add_form(form)
            box.set_box_style(CollapsibleBox.Style.SIMPLE)
            box.header.setVisible(False)
            max_height = max(max_height, self.minimumSizeHint().height())
            box.setVisible(False)
            self.boxes[plugin.name] = box

        self.setMinimumHeight(max_height)

        self.boxes[plugins[0].name].setVisible(True)

    def _plugin_changed(self, plugin_name: str) -> None:
        for name, box in self.boxes.items():
            box.setVisible(name == plugin_name)
