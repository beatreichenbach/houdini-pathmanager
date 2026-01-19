import dataclasses
import fnmatch
import re
from collections.abc import Sequence

from qt_parameters import BoolParameter, ParameterForm, StringParameter

from ..core import schema
from . import base


@dataclasses.dataclass
class Options:
    search: str
    replace: str
    regex: bool
    match_case: bool


class ReplacePlugin(base.Plugin):
    name = 'replace'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None:
        options = Options(**kwargs)

        use_forward_slashes = True

        # TODO: limit only if from is set.

        flags = 0 if options.match_case else re.IGNORECASE
        if options.regex:
            pattern = re.compile(options.search, flags=flags)
            replace = options.replace
        else:
            # The fnmatch case sensitivity depends on OS, so use re.compile.
            pattern_str = fnmatch.translate(options.search)[:-2]
            pattern = re.compile(pattern_str, flags=flags)

            # Escape special characters
            replace = options.replace.encode('unicode_escape').decode('ascii')

        for item in items:
            path = item.path
            try:
                new_path = pattern.sub(replace, path)
            except re.error:
                new_path = ''

            if use_forward_slashes:
                new_path = new_path.replace('\\', '/').replace('//', '/')

            if new_path == path:
                new_path = ''

            # item.preview = self._get_html(path, new_path)
            item.preview = new_path

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

    @staticmethod
    def _get_pattern(search: str, regex: bool, match_case: bool) -> re.Pattern:

        return pattern
