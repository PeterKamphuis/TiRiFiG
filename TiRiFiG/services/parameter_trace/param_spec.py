"""Parameter specification dialog used by add/edit parameter flows."""

from PyQt6 import QtCore, QtWidgets, QtGui

from TiRiFiG.classes.classes import IconButton, icons_location, _center


class ParamSpec(QtWidgets.QWidget):
    """Dialog for selecting parameters and queueing add/edit operations."""

    def __init__(self, par, windowTitle, plotted_parameters=None, addLocation=False,
            parameterTooltips=None, categories=None, disks=None, showInitialValue=False):
        super(ParamSpec, self).__init__()
        self.setProperty("popupBg", True)
        # Enable stylesheet background (needed for border-image on top-level QWidget)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.par = par
        self.parameterTooltips = parameterTooltips if isinstance(parameterTooltips, dict) else {}
        self.categories = categories if isinstance(categories, list) else []
        self.disks = disks if isinstance(disks, list) else []
        self.initialValue = None

        next_row = 0
        if len(self.categories) > 0:
            self.categoryLabel = QtWidgets.QLabel("Category")
            self.category = QtWidgets.QComboBox()
            self.category.addItems(self.categories)
            self.category.setStyleSheet("QComboBox { combobox-popup: 0; }")
            self.category.setMaxVisibleItems(6)
        else:
            self.categoryLabel = None
            self.category = None

        if len(self.disks) > 0:
            self.diskLabel = QtWidgets.QLabel("Disk")
            self.disk = QtWidgets.QComboBox()
            self.disk.addItems(self.disks)
            self.disk.setStyleSheet("QComboBox { combobox-popup: 0; }")
            self.disk.setMaxVisibleItems(6)
        else:
            self.diskLabel = None
            self.disk = None

        self.parameterLabel = QtWidgets.QLabel("Parameter")
        self.parameter = QtWidgets.QComboBox()
        self.parameter.setEditable(True)
        self.parameter.addItem("Select Parameter")
        for i in self.par:
            self.parameter.addItem(i)

        self.parameter.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.parameter.setMaxVisibleItems(6)
        index = self.parameter.findText("Select Parameter", QtCore.Qt.MatchFlag.MatchFixedString)
        self.parameter.setCurrentIndex(index)
        self.parameter.view().setMouseTracking(True)
        self.parameter.view().entered.connect(self._show_parameter_tooltip)
        self.parameter.currentIndexChanged.connect(self._update_parameter_tooltip)
        for i in range(self.parameter.count()):
            item_text = self.parameter.itemText(i).upper().strip()
            if item_text in self.parameterTooltips:
                self.parameter.setItemData(
                    i,
                    self.parameterTooltips[item_text],
                    QtCore.Qt.ItemDataRole.ToolTipRole,
                )
        self.uMeasLabel = QtWidgets.QLabel("Unit Measurement")
        self.unitMeasurement = QtWidgets.QLineEdit()

        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)
        if self.categoryLabel is not None and self.category is not None:
            self.grid.addWidget(self.categoryLabel, next_row, 0)
            self.grid.addWidget(self.category, next_row, 1)
            next_row += 1

        if self.diskLabel is not None and self.disk is not None:
            self.grid.addWidget(self.diskLabel, next_row, 0)
            self.grid.addWidget(self.disk, next_row, 1)
            next_row += 1

        self.grid.addWidget(self.parameterLabel, next_row, 0)
        self.grid.addWidget(self.parameter, next_row, 1)
        next_row += 1
        self.grid.addWidget(self.uMeasLabel, next_row, 0)
        self.grid.addWidget(self.unitMeasurement, next_row, 1)
        next_row += 1

        if showInitialValue:
            self.initialValueLabel = QtWidgets.QLabel("Initial Value")
            self.initialValue = QtWidgets.QLineEdit()
            self.initialValue.setPlaceholderText("Optional")
            self.grid.addWidget(self.initialValueLabel, next_row, 0)
            self.grid.addWidget(self.initialValue, next_row, 1)
            next_row += 1

        self.parameterQueue = None
        self.btnAddParameters = None
        if addLocation:
            self.afterLabel = QtWidgets.QLabel("Add After")
            self.afterParameter = QtWidgets.QComboBox()
            self.afterParameter.setEditable(True)
            self.afterParameter.addItem("End")
            for i in plotted_parameters:
                self.afterParameter.addItem(i)
            self.afterParameter.setStyleSheet("QComboBox { combobox-popup: 0; }")
            self.afterParameter.setMaxVisibleItems(6)
            index = self.afterParameter.findText("End", QtCore.Qt.MatchFlag.MatchFixedString)
            self.afterParameter.setCurrentIndex(index)

            self.grid.addWidget(self.afterLabel, next_row, 0)
            self.grid.addWidget(self.afterParameter, next_row, 1)
            next_row += 1

        self.btnOK = IconButton(icons_location / 'OK.png', self)
        self.btnCancel = IconButton(icons_location / 'cancel.png', self)

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addStretch(1)
        self.hbox.addWidget(self.btnOK)
        if not addLocation:
            self.hbox.addWidget(self.btnCancel)

        self.grid.addLayout(self.hbox, next_row, 0, 1, 2)
        next_row += 1

        if addLocation:
            # Queue area: parameters are added here by OK and can be reordered by drag/drop.
            self.queueLabel = QtWidgets.QLabel("Parameters To Add")
            self.parameterQueue = QtWidgets.QListWidget()
            self.parameterQueue.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
            self.parameterQueue.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
            self.parameterQueue.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
            self.parameterQueue.setMinimumHeight(120)
            self.parameterQueue.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
            self.parameterQueue.customContextMenuRequested.connect(self._queue_context_menu)
            self.parameterQueue.keyPressEvent = self._queue_key_press

            self.btnAddParameters = IconButton(icons_location / 'add_parameters.png', self)
            self.btnAddParameters.setFixedSize(147, 40)
            self.btnAddParameters.setIconSize(QtCore.QSize(147, 40))

            self.grid.addWidget(self.queueLabel, next_row, 0, 1, 2)
            self.grid.addWidget(self.parameterQueue, next_row + 1, 0, 1, 2)

            self.bottomButtons = QtWidgets.QHBoxLayout()
            self.bottomButtons.addWidget(self.btnAddParameters)
            self.bottomButtons.addWidget(self.btnCancel)
            self.grid.addLayout(self.bottomButtons, next_row + 2, 0, 1, 2)

        self.setLayout(self.grid)

        self.setWindowTitle(windowTitle)
        self.setGeometry(300, 300, 360, 420 if addLocation else 180)

        _center(self)
        self.setFocus()

    def _show_parameter_tooltip(self, model_index):
        """Show explanation tooltip while hovering parameter items in the popup."""
        if not model_index.isValid():
            return
        parameter = str(model_index.data()).upper().strip()
        explanation = self.parameterTooltips.get(parameter, "")
        if explanation:
            pos = QtGui.QCursor.pos()
            QtWidgets.QToolTip.showText(pos, explanation, self.parameter.view())

    def _update_parameter_tooltip(self, _idx):
        """Keep combo tooltip in sync with selected parameter explanation."""
        parameter = self.parameter.currentText().upper().strip()
        explanation = self.parameterTooltips.get(parameter, "")
        self.parameter.setToolTip(explanation)

    def remove_queued_parameter(self, row):
        """Remove the item at row from the queue and restore it in the dropdown."""
        if self.parameterQueue is None or row < 0 or row >= self.parameterQueue.count():
            return
        item = self.parameterQueue.takeItem(row)
        data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if isinstance(data, dict):
            parameter = str(data.get('parameter', '')).upper()
            if parameter:
                # Restore the parameter to the dropdown in alphabetical position
                existing = [self.parameter.itemText(i) for i in range(self.parameter.count())]
                if parameter not in existing:
                    insert_idx = 1  # after "Select Parameter"
                    for i in range(1, self.parameter.count()):
                        if self.parameter.itemText(i) > parameter:
                            insert_idx = i
                            break
                    else:
                        insert_idx = self.parameter.count()
                    self.parameter.insertItem(insert_idx, parameter)
                    if parameter in self.parameterTooltips:
                        self.parameter.setItemData(
                            insert_idx,
                            self.parameterTooltips[parameter],
                            QtCore.Qt.ItemDataRole.ToolTipRole,
                        )

    def _queue_key_press(self, event):
        """Delete selected queue item when Delete or Backspace is pressed."""
        if event.key() in (QtCore.Qt.Key.Key_Delete, QtCore.Qt.Key.Key_Backspace):
            row = self.parameterQueue.currentRow()
            if row >= 0:
                self.remove_queued_parameter(row)
        else:
            QtWidgets.QListWidget.keyPressEvent(self.parameterQueue, event)

    def _queue_context_menu(self, pos):
        """Show a context menu with a Remove option for the hovered queue item."""
        item = self.parameterQueue.itemAt(pos)
        if item is None:
            return
        row = self.parameterQueue.row(item)
        menu = QtWidgets.QMenu(self)
        remove_action = menu.addAction("Remove")
        action = menu.exec(self.parameterQueue.viewport().mapToGlobal(pos))
        if action == remove_action:
            self.remove_queued_parameter(row)

    def add_queued_parameter(self, parameter, after_parameter, initial_value=None):
        """Append a parameter with its insertion target to the queue."""
        if self.parameterQueue is None:
            return
        if initial_value is not None and str(initial_value).strip() != "":
            label = f"{parameter} (after: {after_parameter}, init: {initial_value})"
        else:
            label = f"{parameter} (after: {after_parameter})"
        item = QtWidgets.QListWidgetItem(label)
        item.setData(QtCore.Qt.ItemDataRole.UserRole, {
            'parameter': parameter,
            'after': after_parameter,
            'initial_value': initial_value,
        })
        self.parameterQueue.addItem(item)

        # Keep the dropdown in sync with queued parameters.
        idx = self.parameter.findText(parameter, QtCore.Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            self.parameter.removeItem(idx)
        select_idx = self.parameter.findText("Select Parameter", QtCore.Qt.MatchFlag.MatchFixedString)
        if select_idx >= 0:
            self.parameter.setCurrentIndex(select_idx)

    def get_queued_parameters(self):
        """Return queued (parameter, after) tuples in current list order."""
        entries = []
        if self.parameterQueue is None:
            return entries
        for i in range(self.parameterQueue.count()):
            data = self.parameterQueue.item(i).data(QtCore.Qt.ItemDataRole.UserRole)
            if isinstance(data, dict):
                entries.append((
                    str(data.get('parameter', '')).upper(),
                    str(data.get('after', 'End')),
                ))
        return entries

    def get_queued_parameters_with_meta(self):
        """Return queued dict entries including optional initial value."""
        entries = []
        if self.parameterQueue is None:
            return entries
        for i in range(self.parameterQueue.count()):
            data = self.parameterQueue.item(i).data(QtCore.Qt.ItemDataRole.UserRole)
            if isinstance(data, dict):
                entries.append({
                    'parameter': str(data.get('parameter', '')).upper(),
                    'after': str(data.get('after', 'End')),
                    'initial_value': str(data.get('initial_value', '')).strip(),
                })
        return entries
