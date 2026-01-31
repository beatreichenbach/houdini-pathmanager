import os
import logging
from functools import partial

import hou
from qtpy import QtCore, QtWidgets

import pathmanager
from pathmanager.ui import manager

logger = logging.getLogger(__name__)


def screenshot() -> None:
    """Capture a screenshot of the panel for the repository."""

    QtWidgets.QApplication.instance()
    widget = manager.PathManager()
    main_window = hou.qt.mainWindow()
    main_window.widget = widget
    widget.setParent(main_window, QtCore.Qt.WindowType.Tool)
    widget.resize(1280, 720)
    widget.show()

    widget.parameters.set_values(
        {
            'replace': {
                'search': '$HIP/textures',
                'replace': '$HIP/maps',
            },
        }
    )

    QtCore.QTimer.singleShot(0, partial(save_screenshot, widget))


def save_screenshot(widget: QtWidgets.QWidget) -> None:
    pixmap = widget.grab()

    path = os.path.join(
        pathmanager.__file__, '..', '..', '.github', 'assets', 'screenshot.png'
    )
    path = os.path.normpath(path)
    pixmap.save(path)
    logger.info(f'Screenshot saved: {path}')
