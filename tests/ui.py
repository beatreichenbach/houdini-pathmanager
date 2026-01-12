from __future__ import annotations

import tests
from pathmanager.ui import PathManager
from tests import application


def main() -> None:
    with application():
        manager = PathManager()
        manager.show()


if __name__ == '__main__':
    tests.init()
    main()
