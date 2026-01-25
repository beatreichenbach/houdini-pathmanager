from __future__ import annotations

import tests
import sys
from tests import houdini

sys.modules['pathmanager.houdini'] = houdini

from pathmanager.ui.manager import PathManager
from pathmanager.ui.parameters import ParametersWidget
from tests import application


def test_manager() -> None:
    with application():
        manager = PathManager()
        manager.show()


def test_parameters() -> None:
    with application():
        widget = ParametersWidget()
        widget.show()


if __name__ == '__main__':
    tests.init()
    test_manager()
