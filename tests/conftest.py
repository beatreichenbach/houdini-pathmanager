import os
from collections.abc import Iterator

import pytest
from qtpy import QtWidgets


@pytest.fixture(scope='session')
def app() -> Iterator[QtWidgets.QApplication]:
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    application = QtWidgets.QApplication.instance()
    if not isinstance(application, QtWidgets.QApplication):
        application = QtWidgets.QApplication([])
    yield application
