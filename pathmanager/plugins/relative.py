import dataclasses
import enum
from collections.abc import Sequence

from ..core import schema
from pathmanager.qt_parameters import EnumParameter, IntParameter, ParameterForm
from . import base


class AnchorMethod(enum.Enum):
    RELATIVE_HIP = 'Relative to $HIP'
    RELATIVE_JOB = 'Relative to $JOB'
    ABSOLUTE = 'Absolute'


@dataclasses.dataclass
class Options:
    version: int = -1
    pattern: str = 'v(\d+)'


class RelativePlugin(base.Plugin):
    name = 'relative'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None: ...

    def process(self, items: Sequence[schema.Item], kwargs: dict) -> None: ...

    def form(self) -> ParameterForm | None:
        form = ParameterForm('relative')

        formatter = lambda member: member.value

        parm = EnumParameter('mode')
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

        return form
