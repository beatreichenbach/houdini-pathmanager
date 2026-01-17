import dataclasses
import enum
import re
from collections.abc import Sequence

# import hou


class Status(enum.Enum):
    ALL = 'All'
    MISSING = 'Missing'
    FOUND = 'Found'


class ModifyMethod(enum.Enum):
    REPLACE = 'Search and Replace'
    COPY = 'Copy'
    MOVE = 'Move'
    FIND = 'Find Missing'
    VERSION = 'Version'
    RELATIVE = 'Make Relative/Absolute'


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


@dataclasses.dataclass
class Options:
    method: ModifyMethod = ModifyMethod.REPLACE
    replace: Replace = dataclasses.field(default_factory=Replace)
    copy: Copy = dataclasses.field(default_factory=Copy)
    move: Move = dataclasses.field(default_factory=Move)
    find: Find = dataclasses.field(default_factory=Find)
    version: Version = dataclasses.field(default_factory=Version)
    relative: Relative = dataclasses.field(default_factory=Relative)


class Manager:
    def get_items(self) -> tuple[Item, ...]:
        items = []

        for node in hou.node('/').allSubChildren(recurse_in_locked_nodes=False):
            for parm in node.parms():
                template = parm.parmTemplate()
                if isinstance(template, hou.StringParmTemplate):
                    if template.stringType() == hou.stringParmType.FileReference:
                        path = parm.rawValue()

                        if not path:
                            continue

                        parm_type = ParmType(template.fileType())
                        item = Item(
                            name=parm.name(),
                            parm_type=str(parm_type),
                            node_path=node.path(),
                            status='Found',
                            path=path,
                        )

                        preview = path.replace('.png', '.tx')
                        if preview != path:
                            item.preview = preview

                        items.append(item)

        return tuple(items)
