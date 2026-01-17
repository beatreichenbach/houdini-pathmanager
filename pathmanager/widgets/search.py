from __future__ import annotations

from qt_material_icons import MaterialIcon
from qtpy import QtWidgets


class SearchLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setPlaceholderText('Search ...')
        self.setClearButtonEnabled(True)
        clear_button = self.findChild(QtWidgets.QToolButton)
        if isinstance(clear_button, QtWidgets.QToolButton):
            icon = MaterialIcon('close')
            clear_button.setIcon(icon)
