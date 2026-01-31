from qtpy import QtGui, QtWidgets


class DialogButtonBox(QtWidgets.QDialogButtonBox):
    """QDialogButtonBox without the default icons."""

    def setStandardButtons(
        self, buttons: QtWidgets.QDialogButtonBox.StandardButton
    ) -> None:
        """Add Standard Buttons and remove default icons."""

        super().setStandardButtons(buttons)
        for button in self.buttons():
            button.setIcon(QtGui.QIcon())

    def addButton(self, *args, **kwargs) -> QtWidgets.QPushButton:
        """Add Button and remove default icon."""

        button = super().addButton(*args, **kwargs)  # noqa
        if isinstance(button, QtWidgets.QPushButton) and button.icon():
            button.setIcon(QtGui.QIcon())
        return button
