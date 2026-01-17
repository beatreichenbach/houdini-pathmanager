import logging
import os

import tests
from pathmanager.utils import find_files

if __name__ == '__main__':
    tests.init()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data', 'source')

    test_paths = [
        os.path.join(data_dir, 'texture_<UDIM>.png'),
        os.path.join(data_dir, 'sequence.$F.png'),
        os.path.join(data_dir, 'sequence.$F3.png'),
        os.path.join(data_dir, 'sequence.$F4.png'),
        os.path.join(data_dir, 'sequence.###.png'),
        os.path.join(data_dir, 'sequence.####.png'),
        os.path.join(data_dir, 'sequence.%03d.png'),
        os.path.join(data_dir, 'sequence.%04d.png'),
    ]

    for path in test_paths:
        logging.info(f'{path=}')
        files = find_files(path)
        for file in files:
            logging.info(f'    {file}')
