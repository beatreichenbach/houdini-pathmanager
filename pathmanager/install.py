import logging

from qtpy import QtCore, QtGui, QtWidgets

from qt_parameters import CollapsibleBox

logger = logging.getLogger(__name__)

QStyleOptionTab = QtWidgets.QStyleOptionTab


def patch_collapsible_box() -> None:
    if hasattr(CollapsibleBox, '__patched__'):
        return

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        if self._style != CollapsibleBox.Style.BUTTON:
            QtWidgets.QFrame.paintEvent(self, event)
            return

        painter = QtGui.QPainter(self)
        style = self.style()

        if self._collapsed:
            option = QtWidgets.QStyleOptionButton()
            option.initFrom(self)
            if self.underMouse():
                option.state |= QtWidgets.QStyle.StateFlag.State_MouseOver

            element = QtWidgets.QStyle.PrimitiveElement.PE_PanelButtonCommand
            style.drawPrimitive(element, option, painter, self)
        else:
            palette = self.palette()
            color = palette.color(
                QtGui.QPalette.ColorGroup.Normal, QtGui.QPalette.ColorRole.Window
            )

            option = QtWidgets.QStyleOption()
            option.initFrom(self)

            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.setBrush(color.lighter(120))
            painter.drawRect(option.rect)

    CollapsibleBox.paintEvent = paintEvent
    CollapsibleBox.__patched__ = True
    logger.debug(f'Patched {CollapsibleBox.__name__}')
