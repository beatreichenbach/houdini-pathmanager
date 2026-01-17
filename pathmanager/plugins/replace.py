import dataclasses
import fnmatch
import re
from collections.abc import Sequence

from qt_parameters import BoolParameter, ParameterForm, StringParameter

from pathmanager import schema
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

        pattern = self._get_pattern(
            search=options.search,
            regex=options.regex,
            match_case=options.match_case,
        )

        replace = re.escape(options.replace)
        for item in items:
            path = item.path
            new_path = pattern.sub(replace, path)
            if new_path == path:
                new_path = ''
            item.preview = self._get_html(path, new_path)

    def form(self) -> ParameterForm | None:
        form = ParameterForm()

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
        flags = 0 if match_case else re.IGNORECASE
        if regex:
            pattern = re.compile(search, flags=flags)
        else:
            # The fnmatch case sensitivity depends on OS, so use re.compile.
            pattern_str = fnmatch.translate(search)[:-2]
            pattern = re.compile(pattern_str, flags=flags)
        return pattern
