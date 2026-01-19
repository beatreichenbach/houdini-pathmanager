import dataclasses
from collections.abc import Sequence

from pathmanager.core import schema
from pathmanager.qt_parameters import ParameterForm, PathParameter
from . import base


@dataclasses.dataclass
class Options:
    destination: str = ''
    relative_root_enabled: bool = False
    relative_root: str = ''


class MovePlugin(base.Plugin):
    name = 'move'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None: ...

    def process(self, items: Sequence[schema.Item], kwargs: dict) -> None: ...

    def form(self) -> ParameterForm | None:
        form = ParameterForm('move')

        parm = PathParameter('destination')
        parm.set_method(PathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm)

        parm = PathParameter('relative_root')
        parm.set_method(PathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm, checkable=True)

        return form
