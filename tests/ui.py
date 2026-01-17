from __future__ import annotations

import tests
from pathmanager.ui import PathManager
from tests import application
from tests.host import TestHost


def main() -> None:
    with application():
        host = TestHost()
        manager = PathManager()
        manager.set_host(host)

        manager.show()


if __name__ == '__main__':
    tests.init()
    main()
