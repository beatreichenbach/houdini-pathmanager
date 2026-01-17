import dataclasses
import os
import shutil
from collections.abc import Sequence

from pathmanager import schema, utils
from pathmanager.qt_parameters import ParameterForm, PathParameter
from . import base


@dataclasses.dataclass
class Options:
    destination: str = ''
    relative_root_enabled: bool = False
    relative_root: str = ''


class CopyPlugin(base.Plugin):
    name = 'copy'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None:
        options = Options(**kwargs)
        if not options.destination:
            return

        for item in items:
            path = item.path
            if options.relative_root_enabled:
                relative_path = os.path.relpath(path, options.relative_root)
            else:
                relative_path = os.path.basename(path)
            new_path = os.path.join(options.destination, relative_path)

            new_path = new_path.replace('\\', '/').replace('//', '/')

            if new_path == path:
                new_path = ''
            item.preview = new_path

    def process(self, items: Sequence[schema.Item], kwargs: dict) -> None:
        operations = {}

        for item in items:
            if not item.preview:
                continue

            files = utils.find_files(item.path)
            if not files:
                continue

            destination = os.path.dirname(item.preview)
            operations[item.preview] = (files, destination)

        total = sum(len(files) for files, _ in operations.values())

        errored = []

        i = 0
        for preview, (files, destination) in operations.items():
            for src in files:
                self.logger.debug(f'{i / total:04.0%} {src}')
                i += 1

                try:
                    shutil.copy(src, destination)
                except IOError as e:
                    self.logger.error(e)
                    errored.append(preview)

        for item in items:
            if not item.preview in errored and item.preview in operations:
                item.path = item.preview
            item.preview = ''

    def form(self) -> ParameterForm | None:
        form = ParameterForm()

        parm = PathParameter('destination')
        parm.set_method(PathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm)

        parm = PathParameter('relative_root')
        parm.set_method(PathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm, checkable=True)

        return form
