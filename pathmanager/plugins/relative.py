import enum
import os.path
from collections.abc import Sequence

from pathmanager.core import schema
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
        plugin_values = kwargs.get('relative', {})

        mode = plugin_values.get('mode', '')
        parents = plugin_values.get('parents', 0)
        parents_enable = plugin_values.get('parents_enable', False)
        parents = parents * parents_enable

        # Absolute
        if mode == AnchorMethod.ABSOLUTE:
            for item in items:
                path = item.path.raw
                absolute_path = HoudiniHost.expand_string(path, preserve_frame=True)
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
            absolute_path = HoudiniHost.expand_string(path, preserve_frame=True)
            relative_path = os.path.relpath(absolute_path, root)

            # Preserve '..'
            parts = relative_path.split('\\|/')
            count = parts.count('..')

            if count <= parents:
                path = os.path.join(env, relative_path)
                item.set_preview(path)

    def form(self) -> ParameterForm | None:
        form = ParameterForm('relative')

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
