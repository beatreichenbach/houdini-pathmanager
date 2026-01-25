import logging
import os.path
import re
from collections.abc import Sequence

import hou

from pathmanager.core import schema
from . import widgets

logger = logging.getLogger(__name__)


class HoudiniHost:
    def __init__(self) -> None:
        widgets.patch_collapsible_box()

    def get_items(self, selected: bool = False) -> tuple[schema.Item, ...]:
        items = []

        if selected:
            nodes = hou.selectedNodes()
        else:
            nodes = hou.node('/').allSubChildren(recurse_in_locked_nodes=False)

        for node in nodes:
            for parm in node.parms():
                template = parm.parmTemplate()
                if (
                    isinstance(template, hou.StringParmTemplate)
                    and template.stringType() == hou.stringParmType.FileReference
                ):
                    if item := self._get_item(node, parm):
                        items.append(item)

        return tuple(items)

    def update_items(self, items: Sequence[schema.Item]) -> None:
        for item in items:
            if not item.preview.raw:
                continue
            if node := hou.node(item.node_path):
                if parm := node.parm(item.parm_name):
                    parm.set(item.preview.raw)

    @staticmethod
    def _get_item(node: hou.Node, parm: hou.Parm) -> schema.Item | None:
        raw = parm.rawValue()

        if not raw:
            return None

        template = parm.parmTemplate()
        parm_type = HoudiniHost._get_parm_type(template.fileType())
        node_type = schema.NodeType(
            name=node.type().name(),
            category=node.type().category().name(),
        )
        expanded = parm.evalAtFrame(1)
        path = schema.Item.Path(raw=raw, expanded=expanded)

        if '`' in raw:
            status = schema.Statuses.EXPRESSION
        # elif re.search(r'\$F{?\d*|<UDIM>', raw):
        #     status = schema.Statuses.STACK
        elif os.path.exists(expanded):
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
    def _get_parm_type(file_type: hou.fileType) -> schema.ParmType | None:
        parm_types = {
            hou.fileType.Any: schema.ParmTypes.FILE,
            hou.fileType.Geometry: schema.ParmTypes.GEOMETRY,
            hou.fileType.Image: schema.ParmTypes.IMAGE,
            hou.fileType.Directory: schema.ParmTypes.DIRECTORY,
        }
        return parm_types.get(file_type)

        glob_pattern = re.sub(r'<UDIM>|\$F{?\d*}?', '*', self.raw)
        glob_pattern = hou.text.expandString(glob_pattern)

        version_pattern = r'_v(\d+)'
        glob_version = re.sub(version_pattern, '_v*', self.raw)

    @staticmethod
    def expand_string(text: str, preserve_frame: bool = False) -> str:
        if preserve_frame:
            safe = re.sub(r'\$F', r'<F>', text)
            return hou.text.expandString(safe).replace('<F>', '$F')
        else:
            return hou.text.expandString(text)
