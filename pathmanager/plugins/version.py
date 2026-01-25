from collections.abc import Sequence

from qt_parameters import ComboParameter, IntParameter, StringParameter

from pathmanager.core import schema
from qt_parameters import ParameterForm
from . import base


class VersionPlugin(base.Plugin):
    name = 'version'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None: ...

    def form(self) -> ParameterForm | None:
        form = ParameterForm('version')

        mode_parm = ComboParameter('mode')
        mode_parm.set_items({'Latest': -1, 'Earliest': 0, 'Set': 1})
        form.add_parameter(mode_parm)

        version_parm = IntParameter('version')
        version_parm.set_slider_visible(False)
        version_parm.set_default(1)
        version_parm.setVisible(False)
        form.add_parameter(version_parm)

        mode_parm.value_changed.connect(lambda m: version_parm.setVisible(m == 1))

        parm = StringParameter('pattern')
        parm.set_default('_v(\d+)')
        form.add_parameter(parm)

        return form
