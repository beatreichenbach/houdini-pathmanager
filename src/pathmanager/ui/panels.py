from qtpy import QtWidgets

from . import manager

widgets: list[manager.PathManager] = []


def get_manager() -> QtWidgets.QWidget:
    """Return a new widget and store it in the global cache."""

    QtWidgets.QApplication.instance()

    widget = manager.PathManager()
    widgets.append(widget)
    return widget


def reload() -> None:
    """Reload all panel widgets."""

    for widget in widgets:
        try:
            widget.reload()
        except RuntimeError:
            pass
