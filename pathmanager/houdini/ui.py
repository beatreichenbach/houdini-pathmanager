from qtpy import QtWidgets

from pathmanager.houdini import host
from pathmanager.ui import manager

widgets: list[manager.PathManager] = []


def get_manager() -> QtWidgets.QWidget:
    QtWidgets.QApplication.instance()

    widget = manager.PathManager()
    houdini_host = host.HoudiniHost()
    widget.set_host(houdini_host)
    widgets.append(widget)
    return widget


def reload() -> None:
    for widget in widgets:
        try:
            widget.reload()
        except RuntimeError:
            pass
