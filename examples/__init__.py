import contextlib
import logging
import sys
from collections.abc import Generator

from qtpy import QtWidgets

import pathmanager


@contextlib.contextmanager
def application() -> Generator[QtWidgets.QApplication, None]:
    if isinstance(app := QtWidgets.QApplication.instance(), QtWidgets.QApplication):
        yield app
        return

    app = QtWidgets.QApplication(sys.argv)
    yield app
    app.exec()


def init() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger(pathmanager.__name__).setLevel(logging.DEBUG)
