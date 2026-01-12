import dataclasses

from qtpy import QtGui

from pathmanager import meta


class Status(meta.StyledItem): ...


class Statuses(metaclass=meta.IterMeta):
    MISSING = Status('missing', color=QtGui.QColor('#E53935'), icon='cancel')
    FOUND = Status('found', color=QtGui.QColor('#66BB6A'), icon='check_circle')
    EXPRESSION = Status('expression', icon='code')


class ParmType(meta.StyledItem): ...


class ParmTypes(metaclass=meta.IterMeta):
    FILE = ParmType('file', icon='draft')
    IMAGE = ParmType('image', icon='image')
    GEOMETRY = ParmType('geometry', icon='deployed_code')
    DIRECTORY = ParmType('directory', icon='folder')
    STRING = ParmType('string', icon='text_snippet')


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
    status: Status = Statuses.MISSING

    def set_preview(self, path: str) -> None:
        if path == self.path.raw:
            self.preview.raw = ''
        else:
            self.preview.raw = path.replace('\\', '/')
