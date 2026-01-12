from qt_parameters import ParameterWidget
from qtpy import QtCore, QtWidgets

SHORT_LABELS = ('chop', 'cop', 'dop', 'lop', 'shop', 'sop', 'top', 'vop')


class NodeTypeParameter(ParameterWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent=parent)

    def _init_ui(self) -> None:
        self.dropdown = QtWidgets.QComboBox()
        self.dropdown.setEditable(True)
        self.dropdown.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)

        items = ["geometry", "grid", "group", "glass", "vellum", "vdb_visualizer"]
        self.dropdown.addItems(items)

        completer = QtWidgets.QCompleter(items, self)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        self.dropdown.setCompleter(completer)

        self._layout.addWidget(self.dropdown)
