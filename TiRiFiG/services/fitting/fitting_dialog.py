"""Qt dialog used to edit fitting settings for a parameter."""

from PyQt6 import QtCore, QtWidgets

from TiRiFiG.classes.classes import IconButton, icons_location, _center


class FittingFillDialog(QtWidgets.QDialog):
    def __init__(self, parameter, fitting_parameters, fitting_settings):
        super(FittingFillDialog, self).__init__()
        self.setProperty("popupBg", True)
        # Enable stylesheet background (needed for border-image on top-level QWidget)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.parameter = parameter
        self.infoLabel = QtWidgets.QLabel(
            f"Specify fitting settings for parameter {self.parameter}"
        )

        count = 0
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)
        self.grid.addWidget(self.infoLabel, count, 0, 1, 2)
        count += 1
        for key in fitting_parameters:
            if key not in ['VARY', 'VARINDX']:
                setattr(self, f'{key}Label', QtWidgets.QLabel(f"{key}"))
                setattr(self, f'{key}', QtWidgets.QLineEdit())

                if fitting_settings[key] is not None:
                    tmp = getattr(self, f'{key}')
                    tmp.setPlaceholderText(f"{fitting_settings[key]}")
                self.grid.addWidget(getattr(self, f'{key}Label'), count, 0)
                self.grid.addWidget(getattr(self, f'{key}'), count, 1)
                count += 1

        self.hbox = QtWidgets.QHBoxLayout()
        self.btnOK = IconButton(icons_location / 'OK.png', self)
        self.btnCancel = IconButton(icons_location / 'cancel.png', self)
        self.hbox.addWidget(self.btnOK)
        self.hbox.addWidget(self.btnCancel)
        self.grid.addLayout(self.hbox, count, 0, 1, 2)

        self.setLayout(self.grid)

        self.setWindowTitle("Fitting Parameter Specification")
        self.setGeometry(300, 300, 300, 150)

        _center(self)
        self.setFocus()
