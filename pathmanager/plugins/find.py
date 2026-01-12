import fnmatch
import os
import re
from collections import defaultdict
from collections.abc import Sequence

from .. import schema
from pathmanager.houdini import PathParameter
from qt_parameters import ParameterForm
from . import base


class FindPlugin(base.Plugin):
    name = 'find'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None:
        values = kwargs.get('find', {})
        search_root = values.get('root', '')

        if not search_root:
            return

        collection_pattern = re.compile(r'\$F{?\d*}?|<UDIM>')

        # Collect missing files
        missing_items = defaultdict(list)
        for item in items:
            if item.status == schema.Statuses.MISSING:
                filename = os.path.basename(os.path.normpath(item.path.raw))
                pattern = collection_pattern.sub('*', filename)
                missing_items[pattern].append(item)

        if not missing_items:
            return

        # Find missing files
        for root, dirs, files in os.walk(search_root):
            for file, items in tuple(missing_items.items()):
                if fnmatch.filter(files, file):
                    for item in missing_items[file]:
                        filename = os.path.basename(os.path.normpath(item.path.raw))
                        path = os.path.join(root, filename)
                        item.set_preview(path)
                    del missing_items[file]
                    if not missing_items:
                        return

    def form(self) -> ParameterForm | None:
        form = ParameterForm('find')

        parm = PathParameter('root')
        parm.set_method(PathParameter.Method.EXISTING_DIR)
        form.add_parameter(parm)

        return form
