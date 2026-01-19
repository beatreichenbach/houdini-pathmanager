import dataclasses
from collections.abc import Sequence

from ..core import schema
from pathmanager.qt_parameters import ParameterForm, PathParameter
from . import base


@dataclasses.dataclass
class Options:
    root: str = ''


class FindPlugin(base.Plugin):
    name = 'find'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None: ...

    def process(self, items: Sequence[schema.Item], kwargs: dict) -> None: ...

    def form(self) -> ParameterForm | None:
        form = ParameterForm('find')

        parm = PathParameter('root')
        parm.set_method(PathParameter.Method.EXISTING_DIR)
        parm.set_default('$HIP')
        form.add_parameter(parm)

        return form
