import glob
import os
import re
import shutil
from collections.abc import Sequence

from qt_parameters import ParameterForm

from .. import schema
from pathmanager.houdini import HoudiniHost, PathParameter
from . import base


class MovePlugin(base.Plugin):
    name = 'move'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None:
        values = kwargs.get(self.name, {})
        destination = values.get('destination', '')
        relative_root = values.get('relative_root', '')
        relative_root_enabled = values.get('relative_root_enabled', False)

        if not destination:
            return

        for item in items:
            if item.status != schema.Statuses.FOUND:
                continue

            path = item.path.raw
            absolute_path = HoudiniHost.expand_string(path)
            tail = os.path.basename(absolute_path)

            if relative_root_enabled:
                try:
                    relative_path = os.path.relpath(absolute_path, relative_root)
                    # Only preserve relative path if child
                    if '..' not in relative_path:
                        tail = relative_path
                except ValueError:
                    pass

            new_path = os.path.normpath(os.path.join(destination, tail))
            item.set_preview(new_path)

    def process(self, items: Sequence[schema.Item], kwargs: dict) -> None:
        collection_pattern = re.compile(r'\$F{?\d*}?|<UDIM>')

        # Collect operations
        operations = {}
        for item in items:
            if not item.preview.raw:
                continue

            absolute_path = HoudiniHost.expand_string(item.path.raw)
            glob_pattern = collection_pattern.sub('*', absolute_path)
            files = glob.glob(glob_pattern)

            if not files:
                continue

            absolute_preview = HoudiniHost.expand_string(item.preview.raw)
            destination = os.path.dirname(absolute_preview)
            operations[item.preview.raw] = (files, destination)

        # Copy
        total = sum(len(files) for files, _ in operations.values())
        i = 0
        for preview, (files, destination) in operations.items():
            for src in files:
                self.logger.debug(f'{i / total:04.0%} {src}')
                i += 1

                try:
                    shutil.move(src, destination)
                except IOError as e:
                    self.logger.error(e)

    def form(self) -> ParameterForm | None:
        form = ParameterForm(self.name)

        parm = PathParameter('destination')
        parm.set_method(PathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm)

        parm = PathParameter('relative_root')
        parm.set_method(PathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm, checkable=True)

        return form
