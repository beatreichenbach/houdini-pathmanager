from qt_parameters import EnumParameter, ParameterWidget, PathParameter
import hou
from qtpy import QtWidgets


class HoudiniPathParameter(PathParameter):
    def _init_ui(self) -> None:
        self.line = QtWidgets.QLineEdit()
        self.line.editingFinished.connect(self._editing_finished)
        self._layout.addWidget(self.line)

        self.button = hou.qt.FileChooserButton()
        self.button.fileSelected.connect(self._file_selected)
        self._layout.addWidget(self.button)

        self._layout.setStretch(0, 1)
        self.setFocusProxy(self.line)

    def set_value(self, value: str) -> None:
        super().set_value(value)
        self.button.setFileChooserStartDirectory(self._value or self._dir_fallback)

    def set_method(self, method: PathParameter.Method) -> None:
        super().set_method(method)

        if self._method == PathParameter.Method.OPEN_FILE:
            self.button.setFileChooserFilter(hou.fileType.File)
            self.button.setFileChooserMode(hou.fileChooserMode.Read)
        elif self._method == PathParameter.Method.SAVE_FILE:
            self.button.setFileChooserFilter(hou.fileType.File)
            self.button.setFileChooserMode(hou.fileChooserMode.Write)
        elif self._method == PathParameter.Method.EXISTING_DIR:
            self.button.setFileChooserFilter(hou.fileType.Directory)
            self.button.setFileChooserMode(hou.fileChooserMode.Read)
        else:
            return

    def _editing_finished(self) -> None:
        value = self.line.text()
        super().set_value(value)
        self.button.setFileChooserStartDirectory(self._value or self._dir_fallback)

    def _file_selected(self, value: str) -> None:
        if value:
            self.set_value(value)


class HoudiniEnumParameter(EnumParameter):
    def _init_ui(self) -> None:
        self.combo = hou.qt.ComboBox()
        self.combo.currentIndexChanged.connect(self._current_index_changed)
        self.combo.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )

        self._layout.addWidget(self.combo)
        self.setFocusProxy(self.combo)
