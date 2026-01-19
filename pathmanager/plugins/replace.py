import fnmatch
import re
from collections.abc import Sequence

from qt_parameters import BoolParameter, ParameterForm, StringParameter

from pathmanager.core import schema
from . import base


class ReplacePlugin(base.Plugin):
    name = 'replace'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None:
        plugin_values = kwargs.get('replace', {})
        search = plugin_values.get('search', '')
        replace = plugin_values.get('replace', '')
        regex = plugin_values.get('regex', False)
        match_case = plugin_values.get('match_case', False)
        use_forward_slashes = kwargs.get('use_forward_slashes', False)

        if not search:
            return

        try:
            flags = 0 if match_case else re.IGNORECASE
            if regex:
                pattern = re.compile(search, flags=flags)
            else:
                # The fnmatch case sensitivity depends on OS, so use re.compile.
                pattern_str = fnmatch.translate(search)[:-2]
                pattern = re.compile(pattern_str, flags=flags)

                # Escape special characters
                replace = replace.encode('unicode_escape').decode('ascii')
        except re.error:
            for item in items:
                item.preview.error = 'Error in search pattern'
            return

        for item in items:
            path = item.path.raw
            preview = schema.Item.Preview()

            try:
                preview.raw = pattern.sub(replace, path)
            except re.error:
                preview.error = 'Regex error'

            if use_forward_slashes:
                preview.raw = preview.raw.replace('\\', '/').replace('//', '/')

            if preview.raw == path:
                preview.raw = ''

            item.preview = preview

    def form(self) -> ParameterForm | None:
        form = ParameterForm('replace')

        parm = StringParameter('search')
        parm.set_label('From')
        form.add_parameter(parm)

        parm = StringParameter('replace')
        parm.set_label('To')
        form.add_parameter(parm)

        parm = BoolParameter('regex')
        form.add_parameter(parm)

        parm = BoolParameter('match_case')
        form.add_parameter(parm)

        return form
