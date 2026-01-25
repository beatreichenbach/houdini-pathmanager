from qtpy import QtWidgets

from pathmanager.ui import manager

widgets: list[manager.PathManager] = []


def get_manager() -> QtWidgets.QWidget:
    QtWidgets.QApplication.instance()

    widget = manager.PathManager()
    widgets.append(widget)
    return widget


def reload() -> None:
    for widget in widgets:
        try:
            widget.reload()
        except RuntimeError:
            pass
