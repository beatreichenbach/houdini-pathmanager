import sys

from examples import houdini

sys.modules['pathmanager.hosts.houdini'] = houdini

from qtpy import QtWidgets  # noqa: E402

from pathmanager.ui import Parameters, PathManager  # noqa: E402


def test_manager(app: QtWidgets.QApplication) -> None:
    manager = PathManager()
    assert isinstance(manager, QtWidgets.QWidget)


def test_parameters(app: QtWidgets.QApplication) -> None:
    widget = Parameters()
    assert isinstance(widget, QtWidgets.QWidget)
