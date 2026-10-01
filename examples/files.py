import logging

from examples import init
from examples.houdini.host import SOURCE_DIR
from pathmanager.utils import find_files


def main() -> None:
    test_paths = [
        SOURCE_DIR / 'texture_<UDIM>.png',
        SOURCE_DIR / 'sequence.$F.png',
        SOURCE_DIR / 'sequence.$F3.png',
        SOURCE_DIR / 'sequence.$F4.png',
        SOURCE_DIR / 'sequence.###.png',
        SOURCE_DIR / 'sequence.####.png',
        SOURCE_DIR / 'sequence.%03d.png',
        SOURCE_DIR / 'sequence.%04d.png',
    ]

    for path in test_paths:
        logging.info(f'{path=}')
        files = find_files(str(path))
        for file in files:
            logging.info(f'    {file}')


if __name__ == '__main__':
    init()
    main()
