import dataclasses

from .. import utils
from . import meta


class Status(meta.StyledItem): ...


class Statuses(metaclass=meta.IterMeta[Status]):
    MISSING = Status('missing', color='#E53935', icon='cancel')
    FOUND = Status('found', color='#66BB6A', icon='check_circle')
    EXPRESSION = Status('expression', icon='code')


class ParmType(meta.StyledItem): ...


class ParmTypes(metaclass=meta.IterMeta[ParmType]):
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

        def __post_init__(self) -> None:
            self.raw = utils.normalize_path(self.raw)
            self.expanded = utils.normalize_path(self.expanded)

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
        """Set the preview of the item, only if it doesn't match the raw path."""

        normalized_path = utils.normalize_path(path)

        if normalized_path == self.path.raw:
            self.preview.raw = ''
        else:
            self.preview.raw = normalized_path
