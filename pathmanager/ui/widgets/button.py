from __future__ import annotations

from qtpy import QtCore, QtGui, QtWidgets

from pathmanager.qt_material_icons import MaterialIcon


class CheckBoxButton(QtWidgets.QPushButton):
    def __init__(self, text: str = '', parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(text, parent)

        self._icon_size = self.iconSize().width()
        self._icon_off: QtGui.QIcon | QtGui.QPixmap | None = None
        self._icon_on: QtGui.QIcon | QtGui.QPixmap | None = None
        self._palette_off: QtGui.QPalette | None = None
        self._palette_on: QtGui.QPalette | None = None
        top = int(0.25 * self._icon_size)
        self._contents_margins = QtCore.QMargins(0, top, 0, top)

        self.toggled.connect(self._checked_change)
        self.setCheckable(True)
        self.setIcon(MaterialIcon('check_box_outline_blank', fill=True))
        self.setIcon(MaterialIcon('check_box'), True)

    def sizeHint(self) -> QtCore.QSize:
        size_hint = super().sizeHint()
        size_hint += QtCore.QSize(
            self._contents_margins.left() + self._contents_margins.right(),
            self._contents_margins.top() + self._contents_margins.bottom(),
        )
        return size_hint

    def setIcon(self, icon: QtGui.QIcon | QtGui.QPixmap, on: bool = False) -> None:
        if on:
            if self._palette_on and isinstance(icon, MaterialIcon):
                icon.set_color(
                    self._palette_on.color(QtGui.QPalette.ColorRole.ButtonText)
                )
            self._icon_on = icon
        else:
            self._icon_off = icon
            super().setIcon(icon)

    def set_color(self, color: QtGui.QColor | None) -> None:
        palette = self.palette()
        self._palette_off = self.palette()

        if color is None:
            button_color = QtGui.QPalette().color(QtGui.QPalette.ColorRole.Button)
            text_color = QtGui.QPalette().color(QtGui.QPalette.ColorRole.ButtonText)
        else:
            button_color = color.darker(110)
            text_color = self.palette().color(QtGui.QPalette.ColorRole.ButtonText)
            if text_color.valueF() > button_color.valueF() * 0.5:
                text_color = text_color.lighter(150)
            else:
                text_color = text_color.darker(150)

        palette.setColor(QtGui.QPalette.ColorRole.Button, button_color)
        palette.setColor(
            QtGui.QPalette.ColorGroup.Disabled,
            QtGui.QPalette.ColorRole.Button,
            button_color.darker(150),
        )

        palette.setColor(
            QtGui.QPalette.ColorGroup.Normal,
            QtGui.QPalette.ColorRole.ButtonText,
            text_color,
        )
        self.setPalette(palette)
        self._palette_on = palette
        self._update_color()

    def _checked_change(self, checked: bool) -> None:
        # BUG: fusion style does not recognize On/Off for QIcons
        # https://bugreports.qt.io/browse/QTBUG-82110
        icon = self._icon_on if checked else self._icon_off
        if icon is not None:
            super().setIcon(icon)
        self._update_color()

    def _update_color(self) -> None:
        if self._palette_on is None or self._palette_off is None:
            return

        if self.isChecked():
            self.setPalette(self._palette_on)
        else:
            self.setPalette(self._palette_off)
