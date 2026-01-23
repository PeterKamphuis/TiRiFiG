from PyQt6 import QtCore, QtWidgets, QtGui

# Import shared utilities from qt6_launcher
try:
    from importlib.resources import files as import_pack_files
except ImportError:
    from importlib_resources import files as import_pack_files

# Get icon location
icons_location = import_pack_files('TiRiFiG.utilities.icons')

def _center(widget):
    """Centers the window on screen"""
    qr = widget.frameGeometry()
    cp = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
    qr.moveCenter(cp)
    widget.move(qr.topLeft())

class IconButton(QtWidgets.QPushButton):
    def __init__(self, image_path, parent=None, start_grayscale=False, support_three_states=False, extra_icon_path=None):
        super(IconButton, self).__init__('', parent)
        self.setFixedSize(40, 40)
        self.image_path = image_path
        self.original_pixmap = QtGui.QPixmap(str(image_path))
        if extra_icon_path is not None:
            self.original_pixmap_extra = QtGui.QPixmap(str(extra_icon_path))
        self.is_grayscale = start_grayscale
        self.support_three_states = support_three_states
        self.state = 0 if start_grayscale else 1
        
        if start_grayscale:
            self._apply_grayscale()
        else:
            self.setIcon(QtGui.QIcon(self.original_pixmap))
        
        self.setFlat(True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setIconSize(QtCore.QSize(40,40))
    
    def _apply_grayscale(self):
        """Convert icon to grayscale"""
        image = self.original_pixmap.toImage()
        for x in range(image.width()):
            for y in range(image.height()):
                pixel = image.pixelColor(x, y)
                gray = int(0.299 * pixel.red() + 0.587 * pixel.green() + 0.114 * pixel.blue())
                image.setPixelColor(x, y, QtGui.QColor(gray, gray, gray, pixel.alpha()))
        self.setIcon(QtGui.QIcon(QtGui.QPixmap.fromImage(image)))
    
    def _apply_red_glow(self):
        """Apply red glow/overlay to icon"""
        image = self.original_pixmap.toImage()
        for x in range(image.width()):
            for y in range(image.height()):
                pixel = image.pixelColor(x, y)
                red = min(255, pixel.red() + 100)
                green = int(pixel.green() * 0.5)
                blue = int(pixel.blue() * 0.5)
                image.setPixelColor(x, y, QtGui.QColor(red, green, blue, pixel.alpha()))
        self.setIcon(QtGui.QIcon(QtGui.QPixmap.fromImage(image)))
    
    def set_state(self, state):
        """Set button state: 0=grayscale, 1=normal, 2=red glow"""
        self.state = state
        if state == 0:
            self._apply_grayscale()
        elif state == 1:
            self.setIcon(QtGui.QIcon(self.original_pixmap))
        elif state == 2:
            self.setIcon(QtGui.QIcon(self.original_pixmap_extra))
    
    def cycle_state(self):
        """Cycle through states"""
        if self.support_three_states:
            self.state = (self.state + 1) % 3
        else:
            self.state = 1 - self.state
        self.set_state(self.state)
    
    def set_grayscale(self, grayscale):
        """Enable or disable grayscale"""
        self.is_grayscale = grayscale
        if grayscale:
            self._apply_grayscale()
        else:
            self.setIcon(QtGui.QIcon(self.original_pixmap))
    
    def toggle_grayscale(self):
        """Toggle between grayscale and normal"""
        self.is_grayscale = not self.is_grayscale
        self.set_grayscale(self.is_grayscale)

class CustomMessageBox(QtWidgets.QDialog):
    """Custom message dialog that uses IconButton instead of standard buttons."""
    
    def __init__(self, parent, title, message, icon_type="information", buttons="ok"):
        super(CustomMessageBox, self).__init__(parent)
        self.setProperty("popupBg", True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setWindowTitle(title)
        self.result_value = None
        
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(15)
        
        # Message label
        messageLabel = QtWidgets.QLabel(message)
        messageLabel.setWordWrap(True)
        layout.addWidget(messageLabel)
        
        # Button layout
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addStretch()
        
        if buttons == "ok_cancel":
            self.btnOK = IconButton(icons_location/'OK.png', self)
            self.btnOK.clicked.connect(self.accept)
            self.btnCancel = IconButton(icons_location/'cancel.png', self)
            self.btnCancel.clicked.connect(self.reject)
            btnLayout.addWidget(self.btnOK)
            btnLayout.addWidget(self.btnCancel)
        else:  # "ok" only
            self.btnOK = IconButton(icons_location/'OK.png', self)
            self.btnOK.clicked.connect(self.accept)
            btnLayout.addWidget(self.btnOK)
        
        layout.addLayout(btnLayout)
        self.setLayout(layout)
        
        self.setMinimumWidth(300)
        _center(self)
    
    @staticmethod
    def information(parent, title, message):
        """Show information dialog with OK button."""
        dialog = CustomMessageBox(parent, title, message, "information", "ok")
        dialog.exec()
    
    @staticmethod
    def warning(parent, title, message):
        """Show warning dialog with OK/Cancel buttons. Returns True if OK clicked."""
        dialog = CustomMessageBox(parent, title, message, "warning", "ok_cancel")
        return dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted
    
    @staticmethod
    def critical(parent, title, message):
        """Show critical error dialog with OK button."""
        dialog = CustomMessageBox(parent, title, message, "critical", "ok")
        dialog.exec()


class CustomInputDialog(QtWidgets.QDialog):
    """Custom input dialog that uses IconButton instead of standard buttons."""
    
    def __init__(self, parent, title, label):
        super(CustomInputDialog, self).__init__(parent)
        self.setProperty("popupBg", True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setWindowTitle(title)
        
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(15)
        
        # Label
        promptLabel = QtWidgets.QLabel(label)
        promptLabel.setWordWrap(True)
        layout.addWidget(promptLabel)
        
        # Input field
        self.inputField = QtWidgets.QLineEdit()
        layout.addWidget(self.inputField)
        
        # Button layout
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addStretch()
        
        self.btnOK = IconButton(icons_location/'OK.png', self)
        self.btnOK.clicked.connect(self.accept)
        self.btnCancel = IconButton(icons_location/'cancel.png', self)
        self.btnCancel.clicked.connect(self.reject)
        btnLayout.addWidget(self.btnOK)
        btnLayout.addWidget(self.btnCancel)
        
        layout.addLayout(btnLayout)
        self.setLayout(layout)
        
        self.setMinimumWidth(300)
        _center(self)
        
        # Focus on input field
        self.inputField.setFocus()
    
    @staticmethod
    def getText(parent, title, label):
        """Show input dialog and return (text, ok) tuple."""
        dialog = CustomInputDialog(parent, title, label)
        result = dialog.exec()
        return dialog.inputField.text(), result == QtWidgets.QDialog.DialogCode.Accepted
