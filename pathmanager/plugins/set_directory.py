import os
from collections.abc import Sequence

from .. import schema
from pathmanager.houdini import PathParameter
from qt_parameters import ParameterForm
from . import base


class SetDirectoryPlugin(base.Plugin):
    name = 'set_directory'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None:
        directory = kwargs.get(self.name, {}).get('directory', '')

        if not directory:
            return

        for item in items:
            if item.status == schema.Statuses.EXPRESSION:
                continue

            filename = os.path.basename(os.path.normpath(item.path.raw))
            path = os.path.join(directory, filename)
            item.set_preview(path)

    def form(self) -> ParameterForm | None:
        form = ParameterForm(self.name)

        parm = PathParameter(self.name)
        parm.set_method(PathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm)

        return form
