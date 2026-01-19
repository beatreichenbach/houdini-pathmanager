import logging
import os.path
import re
from collections.abc import Sequence

import hou

from pathmanager.core import base, schema
from . import widgets

logger = logging.getLogger(__name__)


class HoudiniHost(base.Host):
    def __init__(self) -> None:
        widgets.patch_collapsible_box()
        # widgets.patch_browser()

    def get_items(self, selected: bool = False) -> tuple[schema.Item, ...]:
        items = []

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
        elif re.search(r'\$F{?\d*|<UDIM>', raw):
            status = schema.Statuses.STACK
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
        if file_type == hou.fileType.Any:
            return schema.ParmTypes.FILE
        if file_type == hou.fileType.Geometry:
            return schema.ParmTypes.GEOMETRY
        if file_type == hou.fileType.Image:
            return schema.ParmTypes.IMAGE
        if file_type == hou.fileType.Directory:
            return schema.ParmTypes.DIRECTORY
        return None
