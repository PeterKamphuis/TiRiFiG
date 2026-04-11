"""Dialog for collecting polynomial fitting settings."""

from PyQt6 import QtCore, QtWidgets

from TiRiFiG.classes.classes import IconButton, icons_location, _center


class PolyFitWindow(QtWidgets.QWidget):
    """Dialog for polynomial degree and boundary/error settings per parameter."""

    def __init__(self, par, yScale=None, mean_val=None,
            lower_boundary=None, upper_boundary=None, min_order=1, max_order=8):
        super(PolyFitWindow, self).__init__()
        self.setProperty("popupBg", True)
        # Enable stylesheet background (needed for border-image on top-level QWidget)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.par = par
        polys = [1, 2, 3, 4, 5, 6, 7, 8]
        self.minDegreeLabel = QtWidgets.QLabel("Min Degree of Polynomial")
        self.minDegree = QtWidgets.QComboBox()

        for degree in polys:
            self.minDegree.addItem(str(degree))
        self.minDegree.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.minDegree.setCurrentIndex(polys.index(min_order))
        self.maxDegreeLabel = QtWidgets.QLabel("Max Degree of Polynomial")
        self.maxDegree = QtWidgets.QComboBox()
        for degree in polys[::-1]:
            self.maxDegree.addItem(str(degree))
        self.maxDegree.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.maxDegree.setCurrentIndex(polys[::-1].index(max_order))
        self.lowerBoundaryLabel = QtWidgets.QLabel("Lower Boundary Limit")
        self.lowerBoundary = QtWidgets.QLineEdit()
        self.lowerBoundary.setPlaceholderText(f"{lower_boundary}")
        self.upperBoundaryLabel = QtWidgets.QLabel("Upper Boundary Limit")
        self.upperBoundary = QtWidgets.QLineEdit()
        self.upperBoundary.setPlaceholderText(f"{upper_boundary}")

        if self.par.split('_')[0] in ['VROT']:
            self.flatOuterRingsLabel = QtWidgets.QLabel("Number of Outer Flat Rings")
            self.flatOuterRings = QtWidgets.QLineEdit()
            self.flatOuterRings.setPlaceholderText("1")
        else:
            self.innerFlatringsLabel = QtWidgets.QLabel("Inner Flat Rings")
            self.innerFlatrings = QtWidgets.QLineEdit()
            self.innerFlatrings.setPlaceholderText("3")
        self.missing_errorLabel = QtWidgets.QLabel("Default Error")
        self.missing_error = QtWidgets.QLineEdit()
        if mean_val is not None:
            self.missing_error.setPlaceholderText(f"{0.1 * mean_val:.4g}")
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)
        self.grid.addWidget(self.minDegreeLabel, 1, 0)
        self.grid.addWidget(self.minDegree, 1, 1)
        self.grid.addWidget(self.maxDegreeLabel, 2, 0)
        self.grid.addWidget(self.maxDegree, 2, 1)
        self.grid.addWidget(self.lowerBoundaryLabel, 3, 0)
        self.grid.addWidget(self.lowerBoundary, 3, 1)
        self.grid.addWidget(self.upperBoundaryLabel, 4, 0)
        self.grid.addWidget(self.upperBoundary, 4, 1)
        self.grid.addWidget(self.missing_errorLabel, 5, 0)
        self.grid.addWidget(self.missing_error, 5, 1)
        if self.par.split('_')[0] in ['VROT']:
            self.grid.addWidget(self.flatOuterRingsLabel, 6, 0)
            self.grid.addWidget(self.flatOuterRings, 6, 1)
        else:
            self.grid.addWidget(self.innerFlatringsLabel, 6, 0)
            self.grid.addWidget(self.innerFlatrings, 6, 1)

        self.btnOK = IconButton(icons_location / 'OK.png', self)
        self.btnCancel = IconButton(icons_location / 'cancel.png', self)

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.btnOK)
        self.hbox.addWidget(self.btnCancel)

        self.grid.addLayout(self.hbox, 7, 0, 1, 2)

        if self.par.split('_')[0] in ['INCL', 'PA']:
            self.warped = QtWidgets.QCheckBox(text="Fit Angular Momentum Vector?")
            self.grid.addWidget(self.warped, 8, 0)

        self.setLayout(self.grid)
        self.setWindowTitle("Polynomial Fit Specification")
        self.setGeometry(300, 300, 300, 150)

        _center(self)
        self.setFocus()
