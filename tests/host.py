import shutil
from typing import Sequence

import tests
from pathmanager.core import Host, schema
from pathmanager.core.schema import Item, NodeType, ParmTypes, Statuses

import os


class TestHost(Host):
    def __init__(self):
        super().__init__()

        self._generate_data()

    def get_items(self, selected: bool = False) -> tuple[Item, ...]:
        current_dir = os.path.dirname(os.path.abspath(__file__))

        source_dir = os.path.join(current_dir, 'data', 'source')
        os.makedirs(source_dir, exist_ok=True)

        items = []

        # Expression
        node_type = NodeType(name='image', category='sop')
        for i in range(2):
            path = Item.Path(
                raw='$HIP/geo/cube/v1/`$OS`.$F4.bgeo.sc',
                expanded='/home/beat/geo/cube/v1/`$OS`.$F4.bgeo.sc',
            )
            item = Item(
                parm_name=f'file',
                parm_type=ParmTypes.FILE,
                node_path=f'/stage/geo_{i}',
                node_type=node_type,
                path=path,
                status=Statuses.EXPRESSION,
            )
            items.append(item)

        # Geometry
        node_type = NodeType(name='image', category='sop')
        for i in range(2):
            item = Item(
                parm_name=f'file',
                parm_type=ParmTypes.GEOMETRY,
                node_path=f'/stage/geo_{i}',
                node_type=node_type,
                path=Item.Path(raw='$HIP/geo/cube/v1/cube.$F4.bgeo.sc'),
                status=Statuses.STACK,
            )
            items.append(item)

            item = Item(
                parm_name=f'file',
                parm_type=ParmTypes.GEOMETRY,
                node_path=f'/stage/geo_{i}',
                node_type=node_type,
                path=Item.Path(raw='$HIP/geo/cube/v2/cube.$F4.bgeo.sc'),
                status=Statuses.MISSING,
            )
            items.append(item)

        # Textures

        node_type = NodeType(name='image', category='sop')

        for i in range(4):
            for j in range(3):
                path = os.path.join(source_dir, f'texture_{i:03d}.png')

                status = os.path.isfile(path)

                item = Item(
                    parm_name=f'file_{i}',
                    parm_type=ParmTypes.IMAGE,
                    node_path=f'/stage/image_{j}',
                    node_type=node_type,
                    path=Item.Path(raw=path),
                    status=Statuses.FOUND,
                )
                items.append(item)

        # UDIM
        path = os.path.join(source_dir, f'texture.<UDIM>.png')
        status = os.path.isfile(path)

        item = Item(
            parm_name=f'file',
            parm_type=ParmTypes.IMAGE,
            node_path='/stage/image',
            node_type=node_type,
            path=Item.Path(raw=path),
            status=Statuses.STACK,
        )
        items.append(item)

        # File sequence
        path = os.path.join(source_dir, f'sequence.$F4.png')
        status = os.path.isfile(path)

        item = Item(
            parm_name=f'file',
            parm_type=ParmTypes.IMAGE,
            node_path='/stage/image',
            node_type=node_type,
            path=Item.Path(raw=path),
            status=Statuses.STACK,
        )
        items.append(item)
        items.append(item)

        return tuple(items)

    def update_items(self, items: Sequence[schema.Item]) -> None:
        for item in items:
            item.path = schema.Item.Path(raw=item.preview.raw)
            item.preview = schema.Item.Preview()

    @staticmethod
    def _generate_data() -> None:
        """
        Generate test data to test support for UDIMs, file sequences, and .tx files.
        """

        current_dir = os.path.dirname(os.path.abspath(__file__))

        source_dir = os.path.join(current_dir, 'data', 'source')
        os.makedirs(source_dir, exist_ok=True)

        destination_dir = os.path.join(current_dir, 'data', 'destination')
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
            path = os.path.join(source_dir, f'texture.{i}.png')
            paths.append(path)

        # File sequence
        for i in range(1, 11):
            path = os.path.join(source_dir, f'sequence.{i:04d}.png')
            paths.append(path)

        for path in paths:
            with open(path, 'w') as f:
                f.write('')


if __name__ == '__main__':
    tests.init()
    host = TestHost()
