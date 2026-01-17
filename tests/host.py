import shutil

import tests
from pathmanager.hosts.base import Host
from pathmanager.schema import Item

import os
import tempfile


class TestHost(Host):
    def get_items(self) -> tuple[Item, ...]:
        current_dir = os.path.dirname(os.path.abspath(__file__))

        source_dir = os.path.join(current_dir, 'data', 'source')
        os.makedirs(source_dir, exist_ok=True)

        items = []
        # Textures
        for i in range(4):
            for j in range(3):
                path = os.path.join(source_dir, f'texture_{i:03d}.png')

                status = os.path.isfile(path)

                item = Item(
                    name=f'file_{i}',
                    parm_type='image',
                    node_path=f'/stage/image_{j}',
                    status=f'{status}',
                    path=path,
                )
                items.append(item)

        # UDIM
        path = os.path.join(source_dir, f'texture.<UDIM>.png')
        status = os.path.isfile(path)

        item = Item(
            name=f'file',
            parm_type='image',
            node_path='/stage/image',
            status=f'{status}',
            path=path,
        )
        items.append(item)

        # File sequence
        path = os.path.join(source_dir, f'sequence.$F4.png')
        status = os.path.isfile(path)

        item = Item(
            name=f'file',
            parm_type='image',
            node_path='/stage/image',
            status=f'{status}',
            path=path,
        )
        items.append(item)

        return tuple(items)

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

            path = os.path.join(source_dir, f'texture_{i:03d}.tx')
            paths.append(path)

        # UDIM
        for i in range(1001, 1025):
            path = os.path.join(source_dir, f'texture.{i}.png')
            paths.append(path)

            path = os.path.join(source_dir, f'texture.{i}.tx')
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
    host._generate_data()
