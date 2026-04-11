"""Scale manager popup for choosing and editing one plotted parameter graph widget."""

from PyQt6 import QtCore, QtWidgets

from TiRiFiG.classes.classes import CustomMessageBox, IconButton, icons_location, _center


class SMWindow(QtWidgets.QWidget):
    """Popup to edit RADI and y-scale bounds for one selected plotted parameter."""

    def __init__(self, graph_widgets, initial_parameter=None):
        super(SMWindow, self).__init__()
        self.setProperty("popupBg", True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)

        self.graph_widgets = list(graph_widgets)
        self.widget_by_parameter = {widget.par: widget for widget in self.graph_widgets}
        self.parameter_name = ""
        self.xMinVal = 0.0
        self.xMaxVal = 0.0
        self.yMinVal = 0.0
        self.yMaxVal = 0.0

        self.parameterLabel = QtWidgets.QLabel("Parameter")
        self.parameter = QtWidgets.QComboBox()
        self.parameter.addItems([widget.par for widget in self.graph_widgets])
        self.parameter.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.parameter.setMaxVisibleItems(6)
        self.parameter.currentIndexChanged.connect(self.onChangeEvent)

        if initial_parameter in self.widget_by_parameter:
            self.parameter.setCurrentText(initial_parameter)

        self.xLabel = QtWidgets.QLabel("RADI")
        self.xMin = QtWidgets.QLineEdit()
        self.xMax = QtWidgets.QLineEdit()

        self.yLabel = QtWidgets.QLabel("Y Scale")
        self.yMin = QtWidgets.QLineEdit()
        self.yMax = QtWidgets.QLineEdit()

        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)
        self.grid.addWidget(self.parameterLabel, 0, 0)
        self.grid.addWidget(self.parameter, 0, 1)
        self.grid.addWidget(self.xLabel, 1, 0)
        self.grid.addWidget(self.xMin, 2, 0)
        self.grid.addWidget(self.xMax, 2, 1)
        self.grid.addWidget(self.yLabel, 3, 0)
        self.grid.addWidget(self.yMin, 4, 0)
        self.grid.addWidget(self.yMax, 4, 1)

        self.hboxBtns = QtWidgets.QHBoxLayout()
        self.hboxBtns.addStretch(1)
        self.btnUpdate = IconButton(icons_location / 'OK.png', self)
        self.btnUpdate.clicked.connect(self.updateScale)
        self.btnCancel = IconButton(icons_location / 'cancel.png', self)
        self.btnCancel.clicked.connect(self.close)
        self.hboxBtns.addWidget(self.btnUpdate)
        self.hboxBtns.addWidget(self.btnCancel)

        self.fbox = QtWidgets.QFormLayout()
        self.fbox.addRow(self.grid)
        self.fbox.addRow(self.hboxBtns)

        self.setLayout(self.fbox)
        self.setWindowTitle("Scale Manager")
        self.setGeometry(300, 300, 320, 150)
        _center(self)
        self.setFocus()

        self.onChangeEvent()

    def _active_widget(self):
        return self.widget_by_parameter.get(self.parameter.currentText())

    def onChangeEvent(self):
        graph_widget = self._active_widget()
        if graph_widget is None:
            return

        self.parameter_name = graph_widget.par
        self.xMinVal = float(graph_widget.xScale[0])
        self.xMaxVal = float(graph_widget.xScale[1])
        self.yMinVal = float(graph_widget.yScale[0])
        self.yMaxVal = float(graph_widget.yScale[1])

        self.xMin.clear()
        self.xMax.clear()
        self.yMin.clear()
        self.yMax.clear()
        self.xMin.setPlaceholderText(f"RADI min ({self.xMinVal:g})")
        self.xMax.setPlaceholderText(f"RADI max ({self.xMaxVal:g})")
        self.yMin.setPlaceholderText(f"{self.parameter_name} min ({self.yMinVal:g})")
        self.yMax.setPlaceholderText(f"{self.parameter_name} max ({self.yMaxVal:g})")
        self.yLabel.setText(self.parameter_name)

    def updateScale(self):
        """Apply entered min/max values to only the current graph widget."""
        graph_widget = self._active_widget()
        if graph_widget is None:
            return

        try:
            if self.xMin.text().strip():
                self.xMinVal = float(self.xMin.text())

            if self.xMax.text().strip():
                self.xMaxVal = float(self.xMax.text())

            if self.yMin.text().strip():
                self.yMinVal = float(self.yMin.text())

            if self.yMax.text().strip():
                self.yMaxVal = float(self.yMax.text())
        except ValueError:
            CustomMessageBox.information(
                self,
                "Information",
                "Invalid scale value. Please enter numeric values (e.g. 0.001 or 1e-4).",
            )
            return

        graph_widget.xScale = [self.xMinVal, self.xMaxVal]
        graph_widget.yScale = [self.yMinVal, self.yMaxVal]
        graph_widget.firstPlot()
        self.close()
        CustomMessageBox.information(self, "Information", "Done!")