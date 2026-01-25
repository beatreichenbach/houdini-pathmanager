from qtpy import QtWidgets

from pathmanager.widgets import Browser


class LogView(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.browser = Browser()
        layout.addWidget(self.browser)
