import dataclasses
import glob
import re
import shutil
from collections.abc import Sequence
from pathlib import Path

from pathmanager.api import schema
from pathmanager.api.host import Host
from pathmanager.api.schema import Item, NodeType, ParmTypes, Statuses
from pathmanager.utils import normalize_path

DATA_DIR = Path(__file__).resolve().parents[2] / 'tests' / 'data'
SOURCE_DIR = DATA_DIR / 'source'
DESTINATION_DIR = DATA_DIR / 'destination'

nodes = []


@dataclasses.dataclass
class Node:
    path: str
    node_path: str


class HoudiniHost(Host):
    def __init__(self) -> None:
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

        shutil.rmtree(DESTINATION_DIR, ignore_errors=True)
        DESTINATION_DIR.mkdir(parents=True, exist_ok=True)

        # Generate files
        paths = []

        # Textures
        for i in range(4):
            path = SOURCE_DIR / f'texture_{i:03d}.png'
            paths.append(path)

        # UDIM
        for i in range(1001, 1025):
            path = SOURCE_DIR / f'texture0.{i}.png'
            paths.append(path)

        for i in range(1001, 1025):
            path = SOURCE_DIR / 'child' / f'texture1.{i}.png'
            paths.append(path)

        # File sequence
        for i in range(1, 11):
            path = SOURCE_DIR / f'sequence.{i:04d}.png'
            paths.append(path)

        # Geo sequence
        for i in range(1, 24):
            path = SOURCE_DIR / f'cube.{i:04d}.bgeo.sc'
            paths.append(path)

        # Versions
        for i in range(1, 4):
            path = SOURCE_DIR / f'v{i:03d}' / f'cube_v{i:03d}.bgeo.sc'
            paths.append(path)

        for i in range(1, 4):
            for j in range(1, 4):
                path = SOURCE_DIR / f'v{i:03d}' / f'cube_v{i:03d}.{j:04d}.bgeo.sc'
                paths.append(path)

        for path in paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('')

    @staticmethod
    def expand_string(text: str, expand_frame: bool = False) -> str:
        text = text.replace('$HIP', '/projects/test/houdini')
        text = text.replace('$JOB', '/projects/test')
        return normalize_path(text)

    @staticmethod
    def expand_files(path: str) -> tuple[str, ...]:
        absolute_path = HoudiniHost.expand_string(path)
        glob_pattern = re.sub(r'\$F{?\d*}?|<UDIM>', '*', absolute_path)
        files = glob.glob(glob_pattern)
        return tuple(sorted(normalize_path(file) for file in files))


def populate_nodes() -> None:
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
            path = str(SOURCE_DIR / f'texture_{i:03d}.png')

            node = Node(
                node_path=f'/stage/material/image_{j}_{i}',
                path=path,
            )
            nodes.append(node)

    # UDIM
    for i in range(2):
        path = str(SOURCE_DIR / f'texture{i}.<UDIM>.png')
        node = Node(
            node_path=f'/stage/material/image_udim_{i}',
            path=path,
        )
        nodes.append(node)

    # File sequence
    path = str(SOURCE_DIR / 'sequence.$F4.png')
    for i in range(2):
        node = Node(
            node_path=f'/stage/material/image_sequence_{i}',
            path=path,
        )
        nodes.append(node)

    # Versions
    node = Node(
        node_path='/stage/geometry_version_0',
        path=str(SOURCE_DIR / 'v001' / 'cube_v001.bgeo.sc'),
    )
    nodes.append(node)

    node = Node(
        node_path='/stage/geometry_version_1',
        path=str(SOURCE_DIR / 'v001' / 'cube_v001.$F4.bgeo.sc'),
    )
    nodes.append(node)

    node = Node(
        node_path='/stage/geometry_version_2',
        path=str(SOURCE_DIR / 'v005' / 'cube_v005.$F4.bgeo.sc'),
    )
    nodes.append(node)


populate_nodes()
