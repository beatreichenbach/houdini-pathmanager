from __future__ import annotations

import tests
from pathmanager.ui.manager import PathManager
from pathmanager.ui.parameters import ParametersWidget
from tests import application
from tests.host import TestHost


def test_manager() -> None:
    with application():
        host = TestHost()
        manager = PathManager()
        manager.set_host(host)

        manager.show()


def test_parameters() -> None:
    with application():
        widget = ParametersWidget()
        widget.show()


if __name__ == '__main__':
    tests.init()
    test_manager()
