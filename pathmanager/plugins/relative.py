import enum
import os.path
import re
from collections.abc import Sequence

from .. import schema
from pathmanager.houdini import HoudiniHost, EnumParameter
from qt_parameters import IntParameter, ParameterForm
from . import base


class AnchorMethod(enum.Enum):
    RELATIVE_HIP = 'Relative to $HIP'
    RELATIVE_JOB = 'Relative to $JOB'
    ABSOLUTE = 'Absolute'


class RelativePlugin(base.Plugin):
    name = 'relative'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None:
        values = kwargs.get(self.name, {})

        mode = values.get('mode', '')
        parents = values.get('parents', 0)

        # Absolute
        if mode == AnchorMethod.ABSOLUTE:
            for item in items:
                path = item.path.raw
                absolute_path = HoudiniHost.expand_string(path)
                item.set_preview(absolute_path)
            return

        # Relative
        if mode == AnchorMethod.RELATIVE_HIP:
            env = '$HIP'
        elif mode == AnchorMethod.RELATIVE_JOB:
            env = '$JOB'
        else:
            return

        root = HoudiniHost.expand_string(env)
        for item in items:
            path = item.path.raw
            absolute_path = HoudiniHost.expand_string(path)
            try:
                relative_path = os.path.relpath(absolute_path, root)
            except ValueError:
                continue

            # Preserve '..'
            parts = re.split(r'[\\/]', relative_path)
            count = parts.count('..')

            if count <= parents:
                path = os.path.join(env, relative_path)
                item.set_preview(path)

    def form(self) -> ParameterForm | None:
        form = ParameterForm(self.name)

        formatter = lambda member: member.value

        method_parm = EnumParameter('mode')
        method_parm.set_enum(AnchorMethod)
        method_parm.set_formatter(formatter)
        form.add_parameter(method_parm)

        parents_parm = IntParameter('parents')
        parents_parm.set_line_min(0)
        parents_parm.set_slider_visible(False)
        form.add_parameter(parents_parm)

        method_parm.value_changed.connect(
            lambda m: parents_parm.setEnabled(
                m in (AnchorMethod.RELATIVE_HIP, AnchorMethod.RELATIVE_JOB)
            )
        )

        return form
