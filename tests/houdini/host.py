import dataclasses
import glob
import os
import re
import shutil
from typing import Sequence

import tests
from pathmanager import schema
from pathmanager.schema import Item, NodeType, ParmTypes, Statuses


nodes = []


@dataclasses.dataclass
class Node:
    path: str
    node_path: str


class HoudiniHost:
    def __init__(self):
        super().__init__()

        self._generate_data()

    def get_items(self, selected: bool = False) -> tuple[Item, ...]:
        items = []
        for node in nodes:
            if '`' in node.path:
                status = Statuses.EXPRESSION
            else:
                files = HoudiniHost.expand_files(node.path)
                if files:
                    status = Statuses.FOUND
                else:
                    status = Statuses.MISSING

            item = Item(
                parm_name='file',
                parm_type=ParmTypes.IMAGE,
                node_path=node.node_path,
                node_type=NodeType('image', 'sop'),
                path=Item.Path(raw=node.path, expanded=node.path),
                status=status,
            )
            items.append(item)
        return tuple(items)

    def update_items(self, items: Sequence[schema.Item]) -> None:
        nodes_data = {node.node_path: node for node in nodes}
        for item in items:
            if item.preview.raw:
                node = nodes_data[item.node_path]
                node.path = item.preview.raw
                print(item.preview.raw)
        print('--')
        for node in nodes:
            print(node.path)

    @staticmethod
    def _generate_data() -> None:
        """
        Generate test data to test support for UDIMs, file sequences, and .tx files.
        """

        tests_dir = os.path.dirname(os.path.abspath(tests.__file__))

        source_dir = os.path.join(tests_dir, 'data', 'source')
        destination_dir = os.path.join(tests_dir, 'data', 'destination')
        shutil.rmtree(destination_dir)
        os.makedirs(destination_dir, exist_ok=True)

        # Generate files
        paths = []

        # Textures
        for i in range(4):
            path = os.path.join(source_dir, f'texture_{i:03d}.png')
            paths.append(path)

        # UDIM
        for i in range(1001, 1025):
            path = os.path.join(source_dir, f'texture0.{i}.png')
            paths.append(path)

        for i in range(1001, 1025):
            path = os.path.join(source_dir, 'child', f'texture1.{i}.png')
            paths.append(path)

        # File sequence
        for i in range(1, 11):
            path = os.path.join(source_dir, f'sequence.{i:04d}.png')
            paths.append(path)

        # Geo sequence
        for i in range(1, 24):
            path = os.path.join(source_dir, f'cube.{i:04d}.bgeo.sc')
            paths.append(path)

        # Versions
        for i in range(1, 4):
            path = os.path.join(source_dir, f'v{i:03d}', f'cube_v{i:03d}.bgeo.sc')
            paths.append(path)

        for i in range(1, 4):
            for j in range(1, 4):
                path = os.path.join(
                    source_dir, f'v{i:03d}', f'cube_v{i:03d}.{j:04d}.bgeo.sc'
                )
                paths.append(path)

        for path in paths:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write('')

    @staticmethod
    def expand_string(text: str, preserve_frame: bool = False) -> str:
        text = text.replace('$HIP', '/projects/test/houdini')
        text = text.replace('$JOB', '/projects/test')
        return text

    @staticmethod
    def expand_files(path: str) -> tuple[str, ...]:
        absolute_path = HoudiniHost.expand_string(path)
        glob_pattern = re.sub(r'\$F{?\d*}?|<UDIM>', '*', absolute_path)
        files = glob.glob(glob_pattern)
        return tuple(sorted(files))


def populate_nodes() -> None:
    tests_dir = os.path.dirname(os.path.abspath(tests.__file__))
    source_dir = os.path.join(tests_dir, 'data', 'source')

    # Expression
    for i in range(2):
        node = Node(
            node_path=f'/stage/expression_{i}',
            path='$HIP/geo/cube/v1/`$OS`.$F4.bgeo.sc',
        )
        nodes.append(node)

    # Geometry
    for i in range(2):
        node = Node(
            node_path=f'/stage/geometry_{i}',
            path='$HIP/geo/cube/v1/cube.$F4.bgeo.sc',
        )
        nodes.append(node)

        node = Node(
            node_path=f'/stage/geometry2_{i}',
            path='$HIP/geo/cube/v2/cube.$F4.bgeo.sc',
        )
        nodes.append(node)

    # Textures
    for i in range(4):
        for j in range(2):
            path = os.path.join(source_dir, f'texture_{i:03d}.png')

            node = Node(
                node_path=f'/stage/material/image_{j}_{i}',
                path=path,
            )
            nodes.append(node)

    # UDIM
    for i in range(2):
        path = os.path.join(source_dir, f'texture{i}.<UDIM>.png')
        node = Node(
            node_path=f'/stage/material/image_udim_{i}',
            path=path,
        )
        nodes.append(node)

    # File sequence
    path = os.path.join(source_dir, f'sequence.$F4.png')
    for i in range(2):
        node = Node(
            node_path=f'/stage/material/image_sequence_{i}',
            path=path,
        )
        nodes.append(node)

    # Versions
    node = Node(
        node_path=f'/stage/geometry_version_0',
        path=os.path.join(source_dir, 'v001', f'cube_v001.bgeo.sc'),
    )
    nodes.append(node)

    node = Node(
        node_path=f'/stage/geometry_version_1',
        path=os.path.join(source_dir, 'v001', f'cube_v001.$F4.bgeo.sc'),
    )
    nodes.append(node)

    node = Node(
        node_path=f'/stage/geometry_version_2',
        path=os.path.join(source_dir, 'v005', f'cube_v005.$F4.bgeo.sc'),
    )
    nodes.append(node)


populate_nodes()
