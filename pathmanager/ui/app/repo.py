import logging
from functools import partial
from pathlib import Path

import hou
from qtpy import QtCore, QtWidgets

from . import manager

logger = logging.getLogger(__name__)


def screenshot() -> None:
    """Capture a screenshot of the panel for the repository."""

    QtWidgets.QApplication.instance()
    widget = manager.PathManager()
    main_window = hou.qt.mainWindow()
    main_window.widget = widget  # ty: ignore[unresolved-attribute]
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

    path = Path(__file__).parents[3] / '.github' / 'assets' / 'screenshot.png'
    pixmap.save(str(path))
    logger.info(f'Screenshot saved: {path}')
