import os
from collections.abc import Sequence

from pathmanager.core import schema
from pathmanager.houdini import HoudiniHost, PathParameter
from qt_parameters import ParameterForm
from . import base


class CopyPlugin(base.Plugin):
    name = 'copy'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None:
        values = kwargs.get('find', {})
        destination = values.get('destination', '')
        relative_root = values.get('relative_root', '')
        relative_root_enabled = values.get('relative_root_enabled', False)

        if not destination:
            return

        for item in items:
            if item.status == schema.Statuses.EXPRESSION:
                continue

            path = item.path.raw
            absolute_path = HoudiniHost.expand_string(path, preserve_frame=True)
            if relative_root_enabled:
                relative_path = os.path.relpath(absolute_path, relative_root)
            else:
                relative_path = os.path.basename(absolute_path)

            new_path = os.path.join(destination, relative_path)
            item.set_preview(new_path)

    def process(self, items: Sequence[schema.Item], kwargs: dict) -> None:
        ...
        # operations = {}
        #
        # for item in items:
        #     if not item.preview:
        #         continue
        #
        #     files = utils.find_files(item.path)
        #     if not files:
        #         continue
        #
        #     destination = os.path.dirname(item.preview)
        #     operations[item.preview] = (files, destination)
        #
        # total = sum(len(files) for files, _ in operations.values())
        #
        # errored = []
        #
        # i = 0
        # for preview, (files, destination) in operations.items():
        #     for src in files:
        #         self.logger.debug(f'{i / total:04.0%} {src}')
        #         i += 1
        #
        #         try:
        #             shutil.copy(src, destination)
        #         except IOError as e:
        #             self.logger.error(e)
        #             errored.append(preview)
        #
        # for item in items:
        #     if not item.preview in errored and item.preview in operations:
        #         item.path = item.preview
        #     item.preview = ''

    def form(self) -> ParameterForm | None:
        form = ParameterForm('copy')

        parm = PathParameter('destination')
        parm.set_method(PathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm)

        parm = PathParameter('relative_root')
        parm.set_method(PathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm, checkable=True)

        return form
