import hou
import logging

from pathmanager.core import base, schema

logger = logging.getLogger(__name__)


class HoudiniHost(base.Host):
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

    @staticmethod
    def _get_item(node: hou.Node, parm: hou.Parm) -> schema.Item | None:
        raw = parm.rawValue()

        if not raw:
            return None

        template = parm.parmTemplate()
        parm_type = schema.ParmType(template.fileType())
        node_type = schema.NodeType(
            name=node.nodeType().name(),
            category=node.nodeType().category().name(),
        )
        path = schema.Item.Path(raw=raw, expanded=parm.evalAtFrame(1))

        item = schema.Item(
            parm_name=parm.name(),
            parm_type=parm_type,
            node_path=node.path(),
            node_type=node_type,
            status=schema.Statuses.MISSING,
            path=path,
        )
        return item
