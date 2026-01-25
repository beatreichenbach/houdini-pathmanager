import fnmatch
import re
from collections.abc import Sequence

from qt_material_icons import MaterialIcon
from qt_parameters import BoolParameter, Label, ParameterForm, StringParameter

from .. import schema
from . import base


class ReplacePlugin(base.Plugin):
    name = 'replace'

    def preview(self, items: Sequence[schema.Item], kwargs: dict) -> None:
        plugin_values = kwargs.get(self.name, {})
        search = plugin_values.get('search', '')
        replace = plugin_values.get('replace', '')
        regex = plugin_values.get('regex', False)
        match_case = plugin_values.get('match_case', False)

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
            return

        for item in items:
            try:
                path = pattern.sub(replace, item.path.raw)
            except re.error:
                continue
            item.set_preview(path)

    def form(self) -> ParameterForm | None:
        form = ParameterForm(self.name)

        search_parm = StringParameter('search')
        search_parm.set_label('From')
        form.add_parameter(search_parm)

        replace_parm = StringParameter('replace')
        replace_parm.set_label('To')
        form.add_parameter(replace_parm)

        regex_parm = BoolParameter('regex')
        form.add_parameter(regex_parm)

        parm = BoolParameter('match_case')
        form.add_parameter(parm)

        label = Label()
        label.set_icon(MaterialIcon('error'))
        label.setVisible(False)
        form.add_widget(label, column=2)

        def _parameter_changed() -> None:
            label.setVisible(False)

            search = search_parm.value()
            replace = replace_parm.value()
            regex = regex_parm.value()

            if regex:
                try:
                    pattern = re.compile(search)
                    pattern.sub(replace, '')
                except re.error as e:
                    label.set_text(f'Regex Error: {e.msg}')
                    label.setVisible(True)

        form.parameter_changed.connect(_parameter_changed)

        return form
