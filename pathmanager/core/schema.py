import dataclasses
from functools import cached_property

from qtpy import QtGui

from pathmanager import meta

GREEN = QtGui.QColor('green')
RED = QtGui.QColor('red')


class Status(meta.StyledItem): ...


class Statuses(metaclass=meta.IterMeta):
    MISSING = Status('missing', color=RED, icon='cancel')
    FOUND = Status('found', color=GREEN, icon='check_circle')
    STACK = Status('stack', color=GREEN, icon='stack')
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
        expanded: str = ''
        tooltip: str = ''
        html: str = ''
        error: str = ''

    parm_name: str
    parm_type: ParmType
    node_path: str
    node_type: NodeType

    path: Path = dataclasses.field(default_factory=Path)
    preview: Preview = dataclasses.field(default_factory=Preview)

    expanded: str = ''
    files: tuple[str, ...] = ()
    status: Status = Statuses.MISSING

    @cached_property
    def versions(self) -> tuple[int, ...]:
        return (0, 1, 2, 3)

    def _get_versions(self, path: str, pattern: str) -> tuple[int, ...]: ...
