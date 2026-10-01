import glob
import logging
import re
from collections.abc import Sequence

import hou

from pathmanager import utils
from pathmanager.api import schema
from pathmanager.api.host import Host

from . import widgets

logger = logging.getLogger(__name__)


class HoudiniHost(Host):
    def __init__(self) -> None:
        widgets.patch_collapsible_box()

    def get_items(self, selected: bool = False) -> tuple[schema.Item, ...]:
        items = []

        if selected:
            nodes = hou.selectedNodes()
        else:
            root = hou.node('/')
            nodes = root.allSubChildren(recurse_in_locked_nodes=False) if root else []

        for node in nodes:
            if isinstance(node, hou.OpNode):
                for parm in node.parms():
                    if item := self._get_item(node, parm):
                        items.append(item)

        return tuple(items)

    def update_items(self, items: Sequence[schema.Item]) -> None:
        for item in items:
            if not item.preview.raw:
                continue
            node = hou.node(item.node_path)
            if isinstance(node, hou.OpNode):
                parm = node.parm(item.parm_name)
                if parm is not None:
                    parm.set(item.preview.raw)

    @staticmethod
    def _get_item(node: hou.Node, parm: hou.Parm) -> schema.Item | None:
        template = parm.parmTemplate()
        if not isinstance(template, hou.StringParmTemplate):
            return None

        raw = parm.rawValue()
        if not raw:
            return None

        if template.stringType() == hou.stringParmType.FileReference:
            parm_type = HoudiniHost._get_parm_type(template.fileType())
            if parm_type is None:
                return None

        # Handle nodes such as LOP Reference, Sublayer
        elif template.stringType() == hou.stringParmType.Regular:
            if 'filepath' not in parm.name():
                return None
            parm_type = schema.ParmTypes.STRING
        else:
            return None

        node_type = schema.NodeType(
            name=node.type().name(),
            category=node.type().category().name(),
        )
        expanded = str(parm.evalAtFrame(1))
        path = schema.Item.Path(raw=raw, expanded=expanded)

        if '`' in raw or '(' in raw:
            status = schema.Statuses.EXPRESSION
        else:
            files = HoudiniHost.expand_files(raw)
            if files:
                status = schema.Statuses.FOUND
            else:
                status = schema.Statuses.MISSING

        item = schema.Item(
            parm_name=parm.name(),
            parm_type=parm_type,
            node_path=node.path(),
            node_type=node_type,
            status=status,
            path=path,
        )
        return item

    @staticmethod
    def _get_parm_type(file_type: hou.EnumValue) -> schema.ParmType | None:
        parm_types = {
            hou.fileType.Any: schema.ParmTypes.FILE,
            hou.fileType.Geometry: schema.ParmTypes.GEOMETRY,
            hou.fileType.Image: schema.ParmTypes.IMAGE,
            hou.fileType.Directory: schema.ParmTypes.DIRECTORY,
        }
        return parm_types.get(file_type)

    @staticmethod
    def expand_string(text: str, expand_frame: bool = False) -> str:
        if expand_frame:
            expanded = hou.text.expandString(text)
        else:
            safe = re.sub(r'\$F', r'<F>', text)
            expanded = hou.text.expandString(safe).replace('<F>', '$F')
        return utils.normalize_path(expanded)

    @staticmethod
    def expand_files(path: str) -> tuple[str, ...]:
        absolute_path = HoudiniHost.expand_string(path)
        glob_pattern = re.sub(r'\$F{?\d*}?|<UDIM>', '*', absolute_path)
        files = glob.glob(glob_pattern)
        return tuple(sorted(utils.normalize_path(file) for file in files))
