import glob
import re
from collections.abc import Sequence
from functools import cache
from typing import Any

from qt_parameters import IntParameter, ParameterForm

from pathmanager.api import schema
from pathmanager.hosts.houdini import ComboParameter, HoudiniHost

from . import base


class VersionPlugin(base.Plugin):
    name = 'version'

    def preview(self, items: Sequence[schema.Item], kwargs: dict[str, Any]) -> None:
        values = kwargs.get(self.name, {})
        mode = values.get('mode', '')
        version = values.get('version', 1)

        for item in items:
            if item.status == schema.Statuses.EXPRESSION:
                continue

            versions = get_versions(item.path.raw)
            if not versions:
                continue

            if mode == 'Latest':
                item.set_preview(sorted(versions.values())[-1])
            elif mode == 'Earliest':
                item.set_preview(sorted(versions.values())[0])
            else:
                item.set_preview(versions.get(version, ''))

    def form(self) -> ParameterForm | None:
        form = ParameterForm(self.name)

        mode_parm = ComboParameter[str]('mode')
        mode_parm.set_items(('Latest', 'Earliest', 'Set'))
        form.add_parameter(mode_parm)

        version_parm = IntParameter('version')
        version_parm.set_slider_visible(False)
        version_parm.set_default(1)
        version_parm.setVisible(False)
        form.add_parameter(version_parm)

        mode_parm.value_changed.connect(lambda m: version_parm.setVisible(m == 'Set'))

        return form


# TODO: refresh cache
@cache
def get_versions(path: str) -> dict[int, str]:
    """Return a dictionary of {version: raw path}."""

    collection_pattern = re.compile(r'\$F{?\d*}?|<UDIM>')
    version_pattern = re.compile(r'([\\/._]v)(\d+)')

    absolute_path = HoudiniHost.expand_string(path)
    glob_pattern = collection_pattern.sub('*', absolute_path)
    glob_pattern = version_pattern.sub(r'\1*', glob_pattern)
    files = glob.glob(glob_pattern)

    versions: dict[int, str] = {}
    for file in files:
        if match := version_pattern.search(file):
            number = int(match.group(2))
            version_path = version_pattern.sub(
                lambda m, num=number: f'{m.group(1)}{num:0{len(m.group(2))}d}', path
            )
            versions[number] = version_path

    return versions
