import dataclasses
import enum

from qt_material_icons import MaterialIcon
from qtpy import QtGui

from . import meta

GREEN = QtGui.QColor('green')
RED = QtGui.QColor('red')


class Status(metaclass=meta.IterMeta):
    ALL = meta.StyledItem('all', icon='circle')
    MISSING = meta.StyledItem('missing', color=RED, icon='circle-cross')
    FOUND = meta.StyledItem('missing', color=GREEN, icon='circle-check')


class AnchorMethod(enum.Enum):
    RELATIVE_HIP = 'Relative to $HIP'
    RELATIVE_JOB = 'Relative to $JOB'
    ABSOLUTE = 'Absolute'


@dataclasses.dataclass
class Item:
    name: str
    parm_type: str
    node_path: str
    status: str
    path: str
    preview: str = ''


class ParmType(metaclass=meta.IterMeta):
    FILE = meta.StyledItem('image', icon='draft')
    IMAGE = meta.StyledItem('image', icon='image')
    GEOMETRY = meta.StyledItem('image', icon='deployed_code')
    DIRECTORY = meta.StyledItem('image', icon='folder')


@dataclasses.dataclass
class Options:
    class ModifyMethod(enum.Enum):
        REPLACE = 'Search and Replace'
        COPY = 'Copy'
        MOVE = 'Move'
        FIND = 'Find Missing'
        VERSION = 'Version'
        RELATIVE = 'Make Relative/Absolute'

    @dataclasses.dataclass
    class Replace:
        search: str
        replace: str
        regex: bool
        match_case: bool

    @dataclasses.dataclass
    class Copy:
        destination: str
        relative_root_enabled: bool
        relative_root: str

    @dataclasses.dataclass
    class Move:
        destination: str
        relative_root_enabled: bool
        relative_root: str

    @dataclasses.dataclass
    class Find:
        root: str

    @dataclasses.dataclass
    class Version:
        version: int
        pattern: str

    @dataclasses.dataclass
    class Relative:
        anchor: AnchorMethod
        parents: int

    method: ModifyMethod = ModifyMethod.REPLACE
    replace: Replace = dataclasses.field(default_factory=Replace)
    copy: Copy = dataclasses.field(default_factory=Copy)
    move: Move = dataclasses.field(default_factory=Move)
    find: Find = dataclasses.field(default_factory=Find)
    version: Version = dataclasses.field(default_factory=Version)
    relative: Relative = dataclasses.field(default_factory=Relative)
