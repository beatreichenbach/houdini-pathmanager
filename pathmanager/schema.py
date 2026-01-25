import dataclasses
import os.path
import re
from functools import cached_property

from qtpy import QtGui

from pathmanager import meta

GREEN = QtGui.QColor('#66BB6A')
RED = QtGui.QColor('#E53935')


class Status(meta.StyledItem): ...


class Statuses(metaclass=meta.IterMeta):
    MISSING = Status('missing', color=RED, icon='cancel')
    FOUND = Status('found', color=GREEN, icon='check_circle')
    EXPRESSION = Status('expression', icon='code')


class ParmType(meta.StyledItem): ...


class ParmTypes(metaclass=meta.IterMeta):
    FILE = ParmType('file', icon='draft')
    IMAGE = ParmType('image', icon='image')
    GEOMETRY = ParmType('geometry', icon='deployed_code')
    DIRECTORY = ParmType('directory', icon='folder')


@dataclasses.dataclass
class NodeType:
    name: str
    category: str


@dataclasses.dataclass
class Item(meta.Sortable):
    @dataclasses.dataclass
    class Path:
        raw: str = ''
        expanded: str = ''

    @dataclasses.dataclass
    class Preview:
        raw: str = ''
        html: str = ''

    parm_name: str
    parm_type: ParmType
    node_path: str
    node_type: NodeType

    path: Path = dataclasses.field(default_factory=Path)
    preview: Preview = dataclasses.field(default_factory=Preview)

    expanded: str = ''
    files: tuple[str, ...] = ()
    status: Status = Statuses.MISSING

    def _refresh_status(self) -> None:
        status = Statuses.MISSING

        if '`' in self.path.raw:
            status = Statuses.EXPRESSION

        if os.path.exists(self.path.expanded):
            status = Statuses.FOUND

        # elif re.search(r'\$F{?\d*|<UDIM>', self.path.raw):
        #     status = Statuses.STACK

        self.status = status

    def set_preview(self, path: str) -> None:
        if path == self.path.raw:
            self.preview.raw = ''
        else:
            self.preview.raw = path.replace('\\', '/')

    def file_glob(self) -> str:
        if self.status == Statuses.EXPRESSION:
            return ''

        pattern = re.sub(r'\$F{?\d*}*|<UDIM>', '*', self.path.raw)
        # pattern = hou.text.expandString(pattern)
        return pattern

    @cached_property
    def versions(self) -> tuple[int, ...]:
        return (0, 1, 2, 3)

    def _get_versions(self, path: str, pattern: str) -> tuple[int, ...]: ...
