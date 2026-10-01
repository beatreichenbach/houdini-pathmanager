import enum
import logging
import os
from typing import Any, Generic, TypeVar

import hou
from qt_parameters import CollapsibleBox, ComboParameter, EnumParameter, PathParameter
from qtpy import QtCore, QtGui, QtWidgets

logger = logging.getLogger(__name__)

T = TypeVar('T')
EnumT = TypeVar('EnumT', bound=enum.Enum)


class HoudiniPathParameter(PathParameter):
    def _init_ui(self) -> None:
        self.line = QtWidgets.QLineEdit()
        self.line.editingFinished.connect(self._editing_finished)
        self._layout.addWidget(self.line)

        self.button: Any = hou.qt.FileChooserButton()
        self.button.fileSelected.connect(self._file_selected)
        self._layout.addWidget(self.button)

        self._layout.setStretch(0, 1)
        self.setFocusProxy(self.line)

    def set_value(self, value: str | os.PathLike[str]) -> None:
        super().set_value(value)
        self.button.setFileChooserStartDirectory(self._value or self._dir_fallback)

    def set_method(self, method: PathParameter.Method) -> None:
        super().set_method(method)

        if self._method == PathParameter.Method.OPEN_FILE:
            self.button.setFileChooserFilter(hou.fileType.Any)
            self.button.setFileChooserMode(hou.fileChooserMode.Read)
        elif self._method == PathParameter.Method.SAVE_FILE:
            self.button.setFileChooserFilter(hou.fileType.Any)
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


class HoudiniComboParameter(ComboParameter[T], Generic[T]):
    def _init_ui(self) -> None:
        self.combo: QtWidgets.QComboBox = hou.qt.ComboBox()
        self.combo.currentIndexChanged.connect(self._current_index_changed)
        self.combo.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )

        self._layout.addWidget(self.combo)
        self.setFocusProxy(self.combo)


class HoudiniEnumParameter(EnumParameter[EnumT], Generic[EnumT]):
    def _init_ui(self) -> None:
        self.combo: QtWidgets.QComboBox = hou.qt.ComboBox()
        self.combo.currentIndexChanged.connect(self._current_index_changed)
        self.combo.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )

        self._layout.addWidget(self.combo)
        self.setFocusProxy(self.combo)


def patch_collapsible_box() -> None:
    """
    Overwrite the paintEvent to use a flat surface as Houdini draws QFrames with
    a beveled line.
    """

    if hasattr(CollapsibleBox, '__patched__'):
        return

    def paint_event(self: CollapsibleBox, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        style = self.style()
        palette = self.palette()
        color = palette.color(
            QtGui.QPalette.ColorGroup.Normal, QtGui.QPalette.ColorRole.Window
        )

        if self._style != CollapsibleBox.Style.BUTTON:
            option = QtWidgets.QStyleOption()
            option.initFrom(self)

            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(color.lighter(120))
            painter.drawRect(option.rect)
            return

        if self._collapsed:
            option = QtWidgets.QStyleOptionButton()
            option.initFrom(self)
            if self.underMouse():
                option.state |= QtWidgets.QStyle.StateFlag.State_MouseOver

            element = QtWidgets.QStyle.PrimitiveElement.PE_PanelButtonCommand
            style.drawPrimitive(element, option, painter, self)
        else:
            option = QtWidgets.QStyleOption()
            option.initFrom(self)

            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(color.lighter(120))
            painter.drawRect(option.rect)

    CollapsibleBox.paintEvent = paint_event
    CollapsibleBox.__patched__ = True  # ty: ignore[unresolved-attribute]
    logger.debug(f'Patched {CollapsibleBox.__name__}')
