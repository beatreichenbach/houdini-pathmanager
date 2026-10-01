import difflib
import html
import logging
from abc import ABC
from collections.abc import Sequence
from typing import Any, cast

from qt_parameters import ParameterForm
from qtpy import QtGui, QtWidgets

from pathmanager import utils
from pathmanager.api import schema


class Plugin(ABC):
    name: str
    label: str = ''

    def __init__(self) -> None:
        if not self.label:
            self.label = utils.title(self.name)

        self.logger = logging.getLogger(
            f'{__package__}.plugins.{self.__class__.__name__}'
        )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}()'

    def preview(self, items: Sequence[schema.Item], kwargs: dict[str, Any]) -> None: ...  # noqa: B027

    def process(self, items: Sequence[schema.Item], kwargs: dict[str, Any]) -> None: ...  # noqa: B027

    def form(self) -> ParameterForm | None:
        return None

    @staticmethod
    def _get_html(str1: str, str2: str) -> str:
        str1 = html.escape(str1)
        str2 = html.escape(str2)

        matcher = difflib.SequenceMatcher(None, str1, str2)
        diff = matcher.get_opcodes()

        palette = QtWidgets.QApplication.palette()
        color = palette.color(QtGui.QPalette.ColorRole.Accent)
        color.setAlphaF(0.5)

        htmlcolor = color_to_html_rgba(color)

        result = []
        for tag, i1, i2, j1, j2 in diff:
            if tag == 'equal':
                result.append(str1[i1:i2])
            elif tag == 'delete':
                pass
            elif tag in ('insert', 'replace'):
                result.append(
                    f'<span style="background-color: {htmlcolor};">{str2[j1:j2]}</span>'
                )
        return ''.join(result)


def color_to_html_rgba(color: QtGui.QColor) -> str:
    r, g, b, a = cast(tuple[int, int, int, int], color.getRgb())
    if a == 255:
        return f'#{r:02x}{g:02x}{b:02x}'
    return f'rgba({r}, {g}, {b}, {a / 255:.2f})'
