# -*- coding: UTF-8 -*-
#########################################################################################
# Author: Samuel (samueltwum1@gmail.com) with MSc supervisors                           #
# Copyright 2018 Samuel N. Twum                                                         #
#                                                                                       #
# GPL license - see LICENSE.txt for details                                             #
#########################################################################################

"""This script here is the GUI (PyQt4) implementation of TiRiFiG which allows users of
TiRiFiC to model tilted-ring parameters before fitting. Instructions on how TiRiFiC works
and everything you need to know about it can be found on the github pages:
http://gigjozsa.github.io/tirific/
As of now the code has been written in Python 2.7. Future considerations would be made to
have it run on Python 3 as well.

variables:
    currPar:  tilted-ring parameter whose graph widget window has focus

functions:
    main  : gets the whole thing started
    _center: centering application windows

classes:
    Timer:
        Class variables:  none

        Instance variables:
            t          (int):              the time(ms) when thread begins.
            hFunction  (function):         function to be executed by thread.
            thread     (function):         initialises and start the thread.

        Functions:
            __init__:                      initialises my instance variables.
            handle_function:               calls the function which the thread is run on.
            start:                         starts the thread.
            cancel:                        stops the thread.

    GraphWidget:
        Class variables:
            redo           (list):         the state of some parameters before undo
                                           action.
            mPress         (list):         x-y values of mouse click.
            mRelease       (list):         x-y values of mouse release.
            mMotion        (list):         x-y values of mouse motion.
            mDblPress      (list):         x-y values of mouse double click.

        Instance variables:
            xScale         (list):         upper and lower limit of x-axis.
            yScale         (list):         upper and lower limit of y-axis.
            unitMeas       (string):       the unit measurement for the parameter.
            par            (string):       a specific tilted-ring parameter.
            parVals        (list):         the values of  variable par (y-values on
                                           graph).
            parValRADI     (list):         the values of RADI (x-values on graph).
            historyList    (list):         the values of parVals for each time a point is
                                           shifted.
            key            (bool):         determines whether or not undo/redo key
                                           combination is pressed.
            numPrecisionX  (int):          the precision point to which a x-values are
                                           saved in.
            numPrecisionY  (int):          the precision point to which a y-values are
                                           saved in.
            canvas         (FigureCanvas): figure canvas where the subplots are made.
            btnAddParam    (QPushButton):  add a new plotted parameter to viewgraph.
            btnEditParam   (QPushButton):  change the parameter plotted to another
                                           parameter.
            btnCloseParam  (QPushButton):  close the parameter selection dialog.

        Functions:
            __init__:                      initialises instance variables and starts
                                           graphWidget.
            changeGlobal:                  change the value of the global parameter
                                           (currPar) to reflect the parameter graphWidget
                                           is plotting.
            getClick:                      assigns x-y value captured from mouse
                                           left-click to mPress list or x-y value of.
                                           captured double click to mDblPress.
            getRelease:                    assigns x-y value captured from mouse release
                                           to mRelease list.
            getMotion:                     assigns x-y value captured from mouse motion
                                           to mMotion list.
            undoKey:                       sends the viewgraph back in history .
            redoKey:                       sends the viewgraph forward in history after
                                           an undo action.
            showInformation:               display information to say history list is
                                           exhausted when too many undo/redo actions are
                                           performed.
            firstPlot:                     produces plot of tilted-ring parameter(s) in
                                           viewgraph after .def file is opened.
            plotFunc:                      produces plot of tilted-ring parameter(s) in
                                           viewgraph when interacting with data points.

    SMWindow:
        Class Variables:  none

        Instance Variables:
            xMinVal        (int):          the value of the min x value of the parameter
                                           in focus.
            xMaxVal        (int):          the value of the max x value of the parameter
                                           in focus.
            par            (list):         list of all tilted-ring parameters
            gwDict         (dictionary):   filtered dictionary with only y-scale
            prevParVal     (string):       previous parameter value.
            parameter      (QComboBox):    drop down of all parameters retrieved from the
                                           variable <par>.
            xLabel         (QLabel):       label for RADI.
            xMin           (QLineEdit):    textbox for entering minimum value for RADI.
            xMax           (QLineEdit):    textbox for entering maximum value for RADI.
            yMin           (QLineEdit):    textbox for entering minimum value for
                                           selected parameter.
            yMax           (QLineEdit):    textbox for entering maximum value for
                                           selected parameter.
            btnUpdate      (QPushButton):  update variables with new values and close
                                           window.
            btnCancel      (QPushButton):  cancel changes and close window.

        Functions:
            __init__:                      initialises instance variables
            onChangeEvent:                 changes values of variables if the current
                                           index of the variable <parameter> changes.

    ParamSpec:
        Class Variables:  none

        Instance Variables:
            par             (list):        list of all tilted-ring parameters from .def
                                           file.
            parameterLabel  (QLabel):      label Parameter
            parameter       (QComboBox):   drop down of all tilted-ring parameters
                                           retrieved from the variable <par>.
            uMeasLabel      (QLabel):      label unit measurement
            unitMeasurement (QLineEdit):   textbox for entering unit measurement for
                                           parameter.
            btnOK           (QPushButton): updates the current parameter plotted to
                                           the new parameter specified.
            btnCancel       (QPushButton): close window

        Functions:
            __init__:                      initialises instance variables

    MainWindow:
        Class Variables:
            key             (string):      determines whether or not undo/redo key has
                                           been pressed.
            ncols           (int):         the number of columns in grid layout where
                                           viewgraphs are created.
            nrows           (int):         the number of rows in grid layout where
                                           viewgraphs are created.
            INSET           (string):      name of data cube retrieved from .def file.
            par             (list):        list of tilted-ring parameters which have
                                           their plots displayed in the viewgraph
            unitMeas        (list):        list of unit measurement for respective
                                           parameters in par list.
            tmpDeffile      (string):      path to temp file which is used to sync entry
                                           of data in text editor to viewgraph.
            gwObjects       (list):        list of graph widget objects each representing
                                           a tilted-ring parameter.
            t               (int):         thread which runs a separate process
                                           (open a text editor).
            scrollWidth     (int):         width of the scroll area.
            scrollHeight    (int):         height of the scroll area.
            before          (int):         time in milliseconds.
            numPrecisionY   (int):         precision in terms of number of decimal points
                                           to which values of parameter are handled.
            numPrecisionX   (int):         precision in terms of number of decimal points
                                           to which values of RADI are handled.
            NUR             (int):         number of rings as indicated in .def file.
            data            (list):        stream of text from .def file.
            parVals         (dictionary):  values of tilted-ring parameters.
            historyList     (dictionary):  values of tilted-ring parameters which have
                                           their values changed.
            xScale          (list):        upper and lower limit values of RADI axis
            yScale          (dictionary):  upper and lower limit values of parameter axis
            mPress          (list):        mouse x,y values when left mouse button is
                                           clicked.
            mRelease        (list):        mouse x,y values when the left mouse button
                                           is released.
            mMotion         (list):        mouse x,y values when mouse is moved.

        Instance Variables:
            cWidget        (QWidget):      central widget (main window).
            btnOpen        (QPushButton):  opens an open dialog box for user to choose
                                           the parameter file.
            scrollArea     (QScrollArea):  scroll area where graph widgets will be
                                           populated.
            mainMenu       (QMenu):        Menu bar with file menu, preference menu and
                                           run menu with each menu having different
                                           actions.

        Functions:
            __init__:                      creates the main window frame and calls the
                                           initUI function.
            initUI:                        initialises instance variables and creates
                                           menus with their actions.
            quitApp:                       closes TiRiFiG.
            cleaunUp:                      initialises class variables.
            getData:                       opens .def file and gets data from the file.
            strType:                       determines the data type of a variable.
            numPrecision:                  determines the floating point precision
                                           currently in .def file and sets it.
            getParameter:                  fetches the data points for the various
                                           tilted-ring parameters.
            openDef:                       calls getData and getParameter and creates the
                                           graph widgets for the default parameters
                                           (VROT, SBR, PA, INCL).
            undoCommand:                   undo last action for the current parameter in
                                           focus.
            redoCommand:                   redo last action for the current parameter in
                                           focus.
            setRowCol:                     specify the number of rows and columns in the
                                           grid layout.
            saveFile:                      save changes to file for one parameter.
            saveAll:                       calls saveFile function to save changes to
                                           file for all parameters.
            saveMessage:                   display information that save was successful.
            saveAs:                        save changes to a new file for one parameter.
            saveAsMessage:                 display information that save as was
                                           successful.
            saveAsAll:                     calls saveAs function to save changes for all
                                           parameters to a new file.
            slotChangeData:                change current viewgraph after making changes
                                           to .def file in text editor.
            animate:                       synchronise actions in text file to viewgraph
                                           with calls to slotChangeData function.
            openEditor:                    open preferred text editor.
            SMobj:                         instantiates the scale manager window and pops
                                           it.
            updateScale:                   updates the values in graph widget from what
                                           was entered in the scale manager window.
            updateMessage:                 displays information to say update was
                                           successful.
            add_parameter_dialog:          instantiates the parameter specfication class and
                                           connects btnOK to paramDef function for GW to be added
            insert_parameter_dialog:       instantiates the parameter specfication class and
                                           connects btnOK to paramDef function for GW to be inserted
            editParaObj:                   instantiates the parameter specfication class and
                                           connects btnOK to editParamDef function.
            paramDef:                      adds specified paramater viewgraph to layout.
            editParamDef:                  changes the parameter plotted in viewgraph to
                                           the specified parameter.
            tirificMessage:                displays information about input data cube not
                                           available in current working directory.
            startTiriFiC:                  starts TiRiFiC from terminal.
"""

# libraries
import os, sys, threading, time, logging
os.environ["QT_API"] = "pyqt6"
from subprocess import Popen as run
from math import ceil
from decimal import Decimal
import numpy as np
import copy
import matplotlib
matplotlib.use("qt5agg")
from matplotlib.backends.backend_qtagg import FigureCanvas
#from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib import style
style.use("seaborn-v0_8")
from PyQt6 import QtCore, QtWidgets,QtGui

# --- Modern theme (QSS) -------------------------------------------------------
def apply_modern_style(app: QtWidgets.QApplication, background_image_path: str | None = None) -> None:
    """Apply a sleek, modern style across the app. Optional background image.

    Args:
        app: QApplication instance
        background_image_path: Optional path to a background image for central areas
    """
    QtWidgets.QApplication.setStyle("Fusion")

    print(background_image_path)
    # Dark palette baseline
    palette = QtGui.QPalette()
    base = QtGui.QColor(37, 37, 38)
    panel = QtGui.QColor(45, 45, 48)
    text = QtGui.QColor(220, 220, 220)
    highlight = QtGui.QColor(14, 122, 254)
    disabled = QtGui.QColor(127, 127, 127)

    palette.setColor(QtGui.QPalette.ColorRole.Window, panel)
    palette.setColor(QtGui.QPalette.ColorRole.WindowText, text)
    palette.setColor(QtGui.QPalette.ColorRole.Base, base)
    palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, panel)
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, panel)
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, text)
    palette.setColor(QtGui.QPalette.ColorRole.Text, text)
    palette.setColor(QtGui.QPalette.ColorRole.Button, panel)
    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, text)
    palette.setColor(QtGui.QPalette.ColorRole.Highlight, highlight)
    palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(255, 255, 255))
    # Disabled
    palette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Text, disabled)
    palette.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.ButtonText, disabled)
    app.setPalette(palette)

    # Core QSS
    bg_image_rule = (
        f"border-image: url('{background_image_path}') 0 0 0 0 stretch stretch;"
        if background_image_path else ""
    )
    popup_image_rule = (
        f"background-image: url('{background_image_path}');"
        f"background-position: center;"
        f"background-attachment: fixed;"
        if background_image_path else "background-image: none;"
    )
    qss = f"""
    QMainWindow {{
        background-color: {panel.name()};
        color: {text.name()};
    }}
    QWidget {{
        background-color: {panel.name()};
        color: {text.name()};
    }}
    #centralWidget {{ 
        {bg_image_rule}
        background-color: {panel.name()};
    }}

    /* Apply background image to dialogs/popups as well */
    QDialog, QMessageBox, QProgressDialog {{
        {popup_image_rule}
        background-color: {panel.name()};
        color: {text.name()};
    }}

    /* Custom popup widgets tagged with popupBg=true */
    QWidget[popupBg="true"] {{
        {popup_image_rule}
        background-color: {panel.name()};
        color: {panel.name()};
    }}
    QLabel{{
        background-color: transparent;
        color: {panel.name()};
    }}

    QMenuBar {{ background-color: {panel.name()}; border: none; }}
    QMenuBar::item {{ padding: 6px 10px; background: transparent; }}
    QMenuBar::item:selected {{ background: rgba(255,255,255,0.06); border-radius: 4px; }}

    QMenu {{ background-color: {panel.name()}; border: 1px solid rgba(255,255,255,0.08); }}
    QMenu::item {{ padding: 6px 12px; }}
    QMenu::item:selected {{ background: rgba(255,255,255,0.08); }}

    QScrollArea {{ border: none; background: transparent; }}
    QScrollArea > QWidget > QWidget {{ background: transparent; }}
    QScrollBar:vertical {{ background: transparent; width: 10px; }}
    QScrollBar::handle:vertical {{ background: rgba(255,255,255,0.18); border-radius: 5px; min-height: 40px; }}
    QScrollBar::handle:vertical:hover {{ background: rgba(255,255,255,0.28); }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; }}
    QScrollBar::handle:horizontal {{ background: rgba(255,255,255,0.18); border-radius: 5px; min-width: 40px; }}
    
    QCheckBox {{ background: transparent; 
        color: {panel.name()};
        }}
    

    QCheckBox::indicator:unchecked {{
        background: transparent;
        background-color: transparent;
        color: white;
        border: 1px solid #5A5A5A;
    }}
    
    
   
    QPushButton {{
        background-color: rgba(255,255,255,0.06);
        border: 0px solid rgba(255,255,255,0.08);
        border-radius: 0px;
        padding: 6px 10px;
        color: {panel.name()};
    }}
    QPushButton:hover {{ background-color: rgba(255,255,255,0.12); }}
    QPushButton:pressed {{ background-color: rgba(255,255,255,0.18); }}
    QPushButton:disabled {{ color: {disabled.name()}; border-color: rgba(255,255,255,0.04); }}

    QLineEdit, QComboBox, QTextEdit {{
        background-color: {text.name()};
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 8px;
        padding: 6px 8px;
        color: {panel.name()};
        selection-background-color: {highlight.name()};
    }}
    QComboBox QAbstractItemView {{
        background-color: {panel.name()};
        border: 1px solid rgba(255,255,255,0.08);
        selection-background-color: rgba(255,255,255,0.10);
    }}

    QToolTip {{
        background: {text.name()};
        color: {panel.name()};
        border: 3px solid rgba(255,255,255,0.12);
        padding: 2px 2px;
        opacity: 230;
    }}
    """
    app.setStyleSheet(qss)

try:
    from importlib.resources import files as import_pack_files
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    # For Py<3.9 files is not available
    from importlib_resources import files as import_pack_files
    
currPar = None
selected_option = None
fit_par = {'VROT':'km s-1',
           'SBR':'Jy km s-1 arcsec-2',
           'INCL':'degrees',
           'PA':'degrees',
           'RADI':'arcsec', 
           'Z0':'arcsec',
           'SDIS':'km s-1',
           'XPOS':'degrees',
           'YPOS':'degrees',
           'VSYS':'km s-1',
           'DVRO':'km s-1 arcsec-1',
           'DVRA':'km s-1 arcsec-1',
           'VRAD':'km s-1'
           
           }
icons_location = import_pack_files('TiRiFiG.utilities.icons')
example_location = import_pack_files('TiRiFiG.utilities.example')
def _center(self):
    """Centers the window

    Keyword arguments:
    self --         main window being displayed i.e. the current instance of the
                    mainWindow class

    Returns:
    None

    With information from the user's desktop, the screen resolution is  gotten
    and the center point is figured out for which the window is placed.
    """
    qr = self.frameGeometry()
    cp = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
    qr.moveCenter(cp)
    self.move(qr.topLeft())

class TimerThread():
    def __init__(self, t, hFunction):
        self.t = t
        self.hFunction = hFunction
        self.thread = threading.Timer(self.t, self.handle_function)

    def handle_function(self):
        self.hFunction()
        self.thread = threading.Timer(self.t, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()

class GraphWidget(QtWidgets.QWidget):
    redo = []
    mPress = [None, None]
    mRelease = [None, None]
    mMotion = [None]
    mDblPress = [None, None]
    last_value = 0
    is_dragging = False
    drag_index = None
    _fit_thread = None
    _fit_worker = None
    _progress = None

    def __init__(self, xScale, yScale, unitMeas, par, parVals,parValsErr, parValRADI,
            key, numPrecisionX, numPrecisionY,initial_width,initial_height):
        super(GraphWidget, self).__init__()
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: transparent;")
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.xScale = xScale
        self.yScale = yScale
        self.unitMeas = unitMeas
        self.par = par
        self.parVals = parVals
        self.originalparVals = copy.deepcopy(parVals)
        self.parValsErr = parValsErr
        self.parValRADI = parValRADI
        #at initialsation this is the same as parVals
        self.historyList = [parVals]
        self.key = key
        self.numPrecisionX = numPrecisionX
        self.numPrecisionY = numPrecisionY
        #self.setFixedSize(initial_width, initial_height)
        # Grid Layout
        grid = QtWidgets.QGridLayout()
        #grid.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        #grid.setStyleSheet("border: 3px solid blue; background-color: rgba(255,0,0,0.1);")
     
        self.setLayout(grid)
        # Canvas and Toolbar
        self.figure = plt.figure()
        self.figure.patch.set_facecolor('none')
       
        self.figure.patch.set_alpha(0.0)

        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background: transparent;")
        # self.canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
        # self.canvas.setFocusPolicy( QtCore.Qt.WheelFocus )
        self.canvas.setFocus()


        self.canvas.mpl_connect('button_press_event', self.getClick)
        self.canvas.mpl_connect('button_release_event', self.getRelease)
        self.canvas.mpl_connect('motion_notify_event', self.getMotion)
        # self.canvas.mpl_connect('key_press_event', self.keyPressed)
        self.figure.subplots_adjust(left=0.15, right=1.0, top=1.0, bottom=0.15)
        self.ax = self.figure.add_subplot(111)
        self.ax.patch.set_facecolor('none')
        self.ax.patch.set_alpha(0.0)

        # Persistent artists for fast updates
        self.line_current = None
        self.line_original = None
        self.err_container = None
        self.background = None  # For blitting

        # Setup blitting: cache background when figure is drawn
        self.canvas.mpl_connect('draw_event', self.on_draw)

        # button to add another tilted-ring parameter to plot
        #self.btnAddParam = QtWidgets.QPushButton('&Add',self)
        #self.btnAddParam.setFixedSize(50, 30)
        #self.btnAddParam.setFlat(True)
        # FIX ME: use icon instead of text
        # self.btnAddParam.setIcon(QtGui.QIcon('utilities/icons/plus.png'))
        #self.btnAddParam.setToolTip('Add Parameter')

        # modify plotted parameter
      
        self.btnEditParam = IconButton(icons_location/'edit.png', self)
        
        
        self.btnFitPoly = IconButton(icons_location/'fitpoly.png', self)
        self.btnFitPoly.clicked.connect(self.changeGlobal)
        self.btnFitPoly.clicked.connect(self.smoothParameter) 
        
        self.btnGroupSelect = IconButton(icons_location/'group.png', self)
        self.btnGroupSelect.clicked.connect(self.changeGlobal)
        self.btnGroupSelect.clicked.connect(self.selectGroups) 
        
        self.btnInterRings = IconButton(icons_location/'interpolate.png', self)
        self.btnInterRings.clicked.connect(self.changeGlobal)
        self.btnInterRings.clicked.connect(self.selectInterRings) 
        
        #self.btnEditParam.setToolTip('Modify plotted parameter')

        self.btnCloseParam = IconButton(icons_location/'close.png', self)
        
        # FIX ME: use icon instead of text
        # self.btnEditParam.setIcon(QtGui.QIcon('utilities/icons/edit.png'))
        self.btnEditParam.setToolTip('Modify plotted parameter')
        self.btnFitPoly.setToolTip('Fit polynomial to data')
        self.btnGroupSelect.setToolTip('Select groups of rings to Fit')
        self.btnInterRings.setToolTip('Select rings to fit while interpolating over the rest')
        self.btnCloseParam.setToolTip('Close Window')

        # Rounded, icon-like buttons
        ctrl_qss = """
        QPushButton {
            background-color: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 16px;
            padding: 6px 10px;
        }
        QPushButton:hover { background-color: rgba(255,255,255,0.14); }
        QPushButton:pressed { background-color: rgba(255,255,255,0.22); }
        """
        #self.btnEditParam.setStyleSheet(ctrl_qss)
        #self.btnFitPoly.setStyleSheet(ctrl_qss)
        #self.btnGroupSelect.setStyleSheet(ctrl_qss)
        #self.btnInterRings.setStyleSheet(ctrl_qss)
        #self.btnCloseParam.setStyleSheet(ctrl_qss)
        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox_right = QtWidgets.QHBoxLayout()
        hbox_right.setContentsMargins(0, 0, 0, 0)
        hbox_right.setSpacing(0)
        
        # Add empty spacer widget to align buttons with plot area
        self.spacer_widget = QtWidgets.QWidget()
        hbox.addWidget(self.spacer_widget)
        
        #hbox.addWidget(self.btnAddParam)
        hbox.addWidget(self.btnEditParam)
        hbox.addWidget(self.btnFitPoly)
        hbox.addWidget(self.btnGroupSelect)
        hbox.addWidget(self.btnInterRings)
        hbox.addStretch()
    
        hbox_right.addStretch()
        hbox_right.addWidget(self.btnCloseParam)
        grid.addLayout(hbox, 0, 0)
        grid.addLayout(hbox_right, 0, 1)
        grid.addWidget(self.canvas, 1, 0, 1, 2)

        self.firstPlot()

    def resizeEvent(self, event):
        """Update spacer widget width to 15% of cell width"""
        super().resizeEvent(event)
        if hasattr(self, 'spacer_widget'):
            self.spacer_widget.setFixedWidth(int(self.width() * 0.15))

    def smoothParameter(self):
        #First we get the desired input
        self.create_polyfit_dialog()
    def selectGroups(self):
        QtWidgets.QMessageBox.information(self,'Information','Group selection not yet implemented.')

    def selectInterRings(self):
        QtWidgets.QMessageBox.information(self,'Information','Selecting the rings to interpolate over not yet implemented.')

    def fitPolynomial(self):
        mindegree = int(self.inp.minDegree.currentText())
        maxdegree = int(self.inp.maxDegree.currentText())


        limits = [0., 0.]
        if self.inp.lowerBoundary.text() != '':
            limits[0] = float(self.inp.lowerBoundary.text())
        if self.inp.upperBoundary.text() != '':
            limits[1] = float(self.inp.upperBoundary.text())
        values = np.array(self.parVals,float)
        errors = np.array(self.parValsErr,float)
        radii = np.array(self.parValRADI,float)
        key = self.par.split('_')[0]
        inner_flatrings = 4
        if key not in ['VROT']:
            if self.inp.innerFlatrings.text() != '':
                inner_flatrings = int(self.inp.innerFlatrings.text())
        
        Configuration = {'DEBUG': True,
                         'DEBUG_FUNCTION':'ALL',
                         'VERBOSE_LOG': False,
                         'VERBOSE_SCREEN': False,
                         'OUTPUTLOG': None,
                         'TIMING': False,
                         'NO_RINGS': len(values),
                         'LAST_RELIABLE_RINGS': [len(values),len(values)],
                        }
        Tirific_Template = {f'{self.par}': values,}

        if key in ['INCL','PA']:
            if self.inp.warped.isChecked():
                #We have to fit the angular momentum function
                print(f'Not yet Working')
                return
        self.inp.close()
        zero_point = None
        if key in ['VROT']:
            zero_point = values[0]
            Configuration['CHANNEL_WIDTH'] = min(errors)
            Configuration['RC_UNRELIABLE'] = len(values)
            if hasattr(self.inp, 'flatOuterRings') and self.inp.flatOuterRings.text() != '':
                Configuration['RC_UNRELIABLE'] = len(values)-int(self.inp.flatOuterRings.text())
            print(Configuration['RC_UNRELIABLE'])

        # Show a modal busy dialog
        self._progress = QtWidgets.QProgressDialog("Fitting polynomial…", None, 0, 0, self)
        self._progress.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self._progress.setAutoClose(False)
        self._progress.setAutoReset(False)
        self._progress.setCancelButton(None)
        self._progress.setMinimumDuration(0)
        self._progress.show()

        # Start worker thread to keep UI responsive
        self._fit_thread = QtCore.QThread(self)

        class FitWorker(QtCore.QObject):
            finished = QtCore.pyqtSignal(object, object)
            errored = QtCore.pyqtSignal(str)

            def __init__(self, Configuration, radii, values, errors, key, par, Tirific_Template, inner_fix, zero_point, limits, allowed_order):
                super().__init__()
                self.Configuration = Configuration
                self.radii = radii
                self.values = values
                self.errors = errors
                self.key = key
                self.par = par
                self.Tirific_Template = Tirific_Template
                self.inner_fix = inner_fix
                self.zero_point = zero_point
                self.limits = limits
                self.allowed_order = allowed_order

            @QtCore.pyqtSlot()
            def run(self):
                try:
                    from pyFAT_astro.Support.modify_template import fit_polynomial
                    fitted_values, final_poly = fit_polynomial(
                        self.Configuration,
                        self.radii,
                        self.values,
                        self.errors,
                        self.key,
                        self.Tirific_Template,
                        inner_fix=self.inner_fix,
                        zero_point=self.zero_point,
                        boundary_limits=self.limits,
                        allowed_order=self.allowed_order,
                        return_order=True,
                    )
                    self.finished.emit(fitted_values, final_poly)
                except Exception as e:
                    self.errored.emit(str(e))

        self._fit_worker = FitWorker(Configuration, radii, values, errors, key, self.par, Tirific_Template, inner_flatrings, zero_point, limits, [mindegree, maxdegree])
        self._fit_worker.moveToThread(self._fit_thread)
        self._fit_thread.started.connect(self._fit_worker.run)

        def _done(fitted_values, final_poly):
            try:
                print(f'We fitted {self.par} with polynomial order {final_poly}')
                print(f'We got these values {fitted_values}')
                self.parVals = fitted_values
                self.key = "Yes"
                self.plotFunc()
            finally:
                if self._progress is not None:
                    self._progress.reset()
                    self._progress.hide()
                    self._progress = None

        def _error(msg: str):
            try:
                QtWidgets.QMessageBox.critical(self, "Fit Error", msg)
            finally:
                if self._progress is not None:
                    self._progress.reset()
                    self._progress.hide()
                    self._progress = None

        self._fit_worker.finished.connect(_done)
        self._fit_worker.errored.connect(_error)
        self._fit_worker.finished.connect(self._fit_thread.quit)
        self._fit_worker.errored.connect(self._fit_thread.quit)
        self._fit_thread.finished.connect(self._fit_worker.deleteLater)
        self._fit_thread.finished.connect(self._fit_thread.deleteLater)

        self._fit_thread.start()
        return
      
    def create_polyfit_dialog(self):
        self.inp = PolyFitWindow(self.par)
        self.inp.show()
        self.inp.btnOK.clicked.connect(self.fitPolynomial)
        self.inp.btnCancel.clicked.connect(self.inp.close)
        return

    def on_draw(self, event):
        """Cache a clean background and re-blit the animated line.

        Ensures `line_current` isn't baked into the cached background after any
        full draw (e.g., initial show/resize or axis changes), keeping blit
        updates correct and visible.
        """
        if self.ax is None or self.canvas is None:
            return

        # Temporarily hide the current line to capture a clean background
        if self.line_current is not None:
            was_visible = self.line_current.get_visible()
            self.line_current.set_visible(False)
            self.background = self.canvas.copy_from_bbox(self.ax.bbox)
            # Restore visibility
            self.line_current.set_visible(was_visible)

            # Immediately re-blit the current line so it appears after full draws
            self.ax.draw_artist(self.line_current)
            self.canvas.blit(self.ax.bbox)
        else:
            # No animated line yet; just cache the background
            self.background = self.canvas.copy_from_bbox(self.ax.bbox)
      
        #self.background = self.canvas.copy_from_bbox(self.ax.bbox)

    def changeGlobal(self, val=None):
        global currPar
        if val == None:
            currPar = None
        else:
            currPar = self.par

    def _almost_equal(self, a, b, rel_tol=5e-2, abs_tol=0.0):
        '''Takes two values return true if they are almost equal'''
        diff = abs(b - a)
        return (diff <= abs(rel_tol * b)) or (diff <= abs_tol)
    
    def _over_and_above(self, a, b, switch):
        '''Takes two values return true if they are far apart'''
        # if input values are the same sign
        if (np.sign(a) == np.sign(b)):
            if switch == 'min':
                return a <= b
            else:
                return a >= b
        else:
            # case1: max +ve and top -ve
            # case2: min -ve and bottom +ve 
            return ((a > 0 and b < 0) or (a < 0 and b > 0))

    def getClick(self, event):
        """Left mouse button is clicked

        Keyword arguments:
        self --         main window being displayed i.e. the current instance of the
                        mainWindow class
        event --        event type

        Returns:
        None

        The xData is captured when the left mouse button is clicked on the canvas
        """
        # on left click in figure canvas, captures mouse press and assign None to
        # mouse release

       
        if event.button == 1 and not event.xdata is None:
            self.mPress[0] = event.xdata
            self.mPress[1] = event.ydata
            self.mRelease[0] = None
            self.mRelease[1] = None
            self.is_dragging = True
            # identify closest point to drag
            try:
                distances = [abs(event.xdata - x) for x in self.parValRADI]
                j = int(np.argmin(distances))
                # require it to be within a small x-threshold (similar to previous logic)
                if abs(event.xdata - self.parValRADI[j]) <= 3:
                    self.drag_index = j
                else:
                    self.drag_index = None
            except Exception:
                self.drag_index = None

        if event.dblclick and not event.xdata is None:
            self.mDblPress[0] = event.xdata
            self.mDblPress[1] = event.ydata

            text, ok = QtWidgets.QInputDialog.getText(self, 'Input Dialog',
                                                  'Enter new node value:')
            if ok:
                if text:
                    newVal = float(str(text))
                    for j in range(len(self.parValRADI)):
                        if ((self.mDblPress[0] < (self.parValRADI[j])+3) and
                            (self.mDblPress[0] > (self.parValRADI[j])-3)):

                            self.parVals[j] = newVal
                            bottom, top = self.ax.get_ylim()
                            self.ax.clear()
                            self.ax.set_xlim(self.xScale[0], self.xScale[1])
                            max_yvalue = max(self.parVals)
                            min_yvalue = min(self.parVals)

                            if self._over_and_above(min_yvalue, bottom, 'min'):
                                bottom = min_yvalue - (0.1*(max_yvalue-min_yvalue))
                                # this line is optional, only bottom scale should change
                                top = max_yvalue + (0.1*(max_yvalue-min_yvalue))
                            elif self._over_and_above(max_yvalue, top, 'max'):
                                top = max_yvalue + (0.1*(max_yvalue-min_yvalue))
                                # this line is optional, only top scale should change
                                bottom = min_yvalue - (0.1*(max_yvalue-min_yvalue))
                            elif self._almost_equal(min_yvalue, bottom, rel_tol=1e-2):
                                bottom = min_yvalue - (0.1*(max_yvalue-min_yvalue))
                                # this line is optional, only bottom scale should change
                                top = max_yvalue + (0.1*(max_yvalue-min_yvalue))
                            elif self._almost_equal(max_yvalue, top, rel_tol=1e-2):
                                top = max_yvalue + (0.1*(max_yvalue-min_yvalue))
                                # this line is optional, only top scale should change
                                bottom = min_yvalue - (0.1*(max_yvalue-min_yvalue))

                            self.ax.set_ylim(bottom, top)
                            self.ax.set_xlabel("RADI (arcsec)")
                            self.ax.set_ylabel(self.par + "( "+self.unitMeas+ " )")
                            self.ax.plot(self.parValRADI, self.parVals, '--bo')
                            self.ax.set_xticks(self.parValRADI)
                            self.canvas.draw()
                            self.key = "No"
                            break

                    # append the new point to the history if the last item in history differs
                    # from the new point
                    if not self.historyList[len(self.historyList)-1] == self.parVals[:]:
                        self.historyList.append(self.parVals[:])

            self.mPress[0] = None
            self.mPress[1] = None

    def getRelease(self, event):
        """Left mouse button is released

        Keyword arguments:
        self --         main window being displayed i.e. the current instance of the
                        mainWindow class
        event --        event type

        Returns:
        None

        The xData is captured when the left mouse button is released on the canvas.
        The new data point is added to the history and mouse pressed is assigned None
        """
        # re-look at this logic --seems to be a flaw somewhere


        if not event.ydata is None:
            self.mRelease[0] = event.xdata
            self.mRelease[1] = event.ydata
            self.changeGlobal()
            self.redo = []

        # append the new point to the history if the last item in history differs
        # from the new point
        if not np.array_equal(self.historyList[len(self.historyList)-1], self.parVals[:]):
            self.historyList.append(self.parVals[:])

        self.mPress[0] = None
        self.mPress[1] = None
        self.is_dragging = False
        self.drag_index = None

    def getMotion(self, event):
        """Mouse is in motion

        Keyword arguments:
        self --         main window being displayed i.e. the current instance of the
                        mainWindow class
        event --        event type

        Returns:
        None
        """
        # whilst the left mouse button is being clicked
        # capture the VROT (y-value) during mouse
        # movement and call re-draw graph
        if self.is_dragging:
            # if the mouse pointer moves out of the figure canvas use
            # the last value to redraw the graph
            if event.ydata is None:
                self.last_value += 0.1 * self.last_value
                self.mMotion[0] = self.last_value
            else:
                self.last_value = event.ydata
                self.mMotion[0] = event.ydata
            self.plotFunc()

    def undoKey(self):
        """Key is pressed

        Keyword arguments:
        self --         main window being displayed i.e. the current instance of the
                        mainWindow class
        event --        event type

        Returns:
        None

        Deletes the last item in the history list when "Ctrl+z" is pressed and
        re-draws graph
        """
        if len(self.historyList) > 1:
            self.redo.append([self.numPrecisionY, self.parVals[:],
                              self.historyList[-1], self.yScale[:]])
            self.historyList.pop()
            self.parVals = self.historyList[-1][:]
            self.key = "Yes"
            self.plotFunc()
        else:
            self.showInformation()

    def redoKey(self):
        """Key is pressed

        Keyword arguments:
        self --         main window being displayed i.e. the current instance of the
                        mainWindow class
        event --        event type

        Returns:
        None

        Deletes the last item in the history list when "Ctrl+z" is pressed and
        re-draws graph
        """

        if len(self.redo) > 0:
            self.numPrecisionY = self.redo[-1][2]
            self.parVals = self.redo[-1][3][:]
            self.historyList.append(self.redo[-1][4][:])
            self.yScale = self.redo[-1][5][:]
            self.redo.pop()
            self.key = "Yes"
            self.plotFunc()
        else:
            self.showInformation()


    def showInformation(self):
        """Show the information message

        Keyword arguments:
        self --         main window being displayed i.e. the current instance of the
        mainWindow class

        Returns:
        None

        Displays a messagebox that informs user there's no previous action to be undone
        """
        QtWidgets.QMessageBox.information(self, "Information", "History list is exhausted")


    def firstPlot(self):
        """Plots data from file

        Keyword arguments:
        self --         main window being displayed i.e. the current instance of the
        mainWindow class

        Returns:
        None

        Produces view graph from historyList
        """
      
        self.ax.clear()
        self.ax.set_xlim(self.xScale[0], self.xScale[1])
        self.ax.set_ylim(self.yScale[0], self.yScale[1])
        self.ax.set_xlabel("RADI (arcsec)")
        self.ax.set_ylabel(self.par + "( "+self.unitMeas+ " )")

        # Create persistent artists once, then update data
       
        (self.line_current,) = self.ax.plot(self.parValRADI, self.parVals, '--bo', zorder=4,animated=True)
   
       
        self.ax.plot(self.parValRADI, self.originalparVals, '--ro', alpha=0.2, zorder=2)
        self.ax.errorbar(
                self.parValRADI,
                self.originalparVals,
                yerr=self.parValsErr,
                c='r', linestyle='-', alpha=0.2, zorder=2
            )
       
        self.ax.set_xticks(self.parValRADI)
        #Make sure to catch the current line in the limits
        if self.line_current is not None:
            self.line_current.set_visible(True)
            self.canvas.draw()
        ylimits = self.ax.get_ylim()
        # Hide the animated line before the full draw to keep background clean
        if self.line_current is not None:
            self.line_current.set_visible(False)
        # Full draw for non-animated artists (axes, error bars, originals)
        self.ax.set_ylim(ylimits[0], ylimits[1])
        self.canvas.draw()
        # Cache clean background and then re-blit the current line
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        #if self.line_current is not None:
        self.line_current.set_visible(True)
        self.ax.draw_artist(self.line_current)
        self.canvas.blit(self.ax.bbox)
        self.canvas.flush_events()
        self.key = "No"

    def plotFunc(self):
        """Plots data from file

        Keyword arguments:
        self --         main window being displayed i.e. the current instance of the
                        mainWindow class

        Returns:
        None

        Produces view graph from historyList or parVals
        """

        if self.key == "Yes":
          
            self.firstPlot()

        # this re-plots the graph as long as the mouse is in motion and the right data
        # point is clicked
        else:
            # Fast path: update only the dragged point and line data
            if self.is_dragging and self.drag_index is not None and self.mMotion[0] is not None:
                j = self.drag_index
                # set the y-value directly to current mouse y
                new_y = self.mMotion[0]
                if new_y is not None:
                    self.parVals[j] = new_y

                    # Update current line data only
                    self.line_current.set_ydata(self.parVals)

                    # Adjust limits only if new point is outside current view
                    bottom, top = self.ax.get_ylim()
                    if new_y < bottom or new_y > top:
                        max_yvalue = float(np.max(self.parVals))
                        min_yvalue = float(np.min(self.parVals))
                        span = max(1e-9, (max_yvalue - min_yvalue))
                        bottom = min_yvalue - 0.1 * span
                        top = max_yvalue + 0.1 * span
                        self.ax.set_ylim(bottom, top)
                        self.background = None  # Invalidate cached background
                        self.canvas.draw_idle()
                    else:    
                        # Blit-accelerated redraw (only changed region)
                        if self.background is not None:
                            self.canvas.restore_region(self.background) 
                            self.ax.draw_artist(self.line_current)
                            self.canvas.blit(self.ax.bbox)
                            self.canvas.flush_events()
                        else:
                            self.canvas.draw_idle()
                    self.key = "No"
            # If not dragging, do nothing heavy here

class SMWindow(QtWidgets.QWidget):

    def __init__(self, par, xVal, gwObjects):
        # TODO SAM (26/06/2019) no need to pass 'par' to init if we have 'gwObjects'
        # but maybe we need it because it makes things faster
        super(SMWindow, self).__init__()
        self.setProperty("popupBg", True)
        # Enable stylesheet background (needed for border-image on top-level QWidget)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.xMinVal = xVal[0]
        self.xMaxVal = xVal[1]
        self.gwObjects = gwObjects
        self.par = par
        self.prevParVal = ""
        self.counter = 0

        self.parameter = QtWidgets.QComboBox()
        # self.parameter.setEditable(True)
        self.parameter.addItem("Select Parameter")
        for i in self.par:
            self.parameter.addItem(i)
        # self.parameter.setAutoCompletion(True) : doesn't work in PyQt5
        self.parameter.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.parameter.setMaxVisibleItems(5)
        index = self.parameter.findText("Select Parameter", 
            QtCore.Qt.MatchFlag.MatchFixedString)
        self.parameter.setCurrentIndex(index)
        self.parameter.currentIndexChanged.connect(self.onChangeEvent)
        # run a for loop here to gather all they loaded parameters and populate as many text boxes

        self.xLabel = QtWidgets.QLabel("RADI")
        self.xMin = QtWidgets.QLineEdit()
        self.xMin.setPlaceholderText("RADI min ("+str(self.xMinVal)+")")
        self.xMax = QtWidgets.QLineEdit()
        self.xMax.setPlaceholderText("RADI max ("+str(self.xMaxVal)+")")
        self.xGrid = QtWidgets.QGridLayout()
        self.xGrid.setSpacing(10)
        self.xGrid.addWidget(self.xLabel, 1, 0)
        self.xGrid.addWidget(self.xMin, 2, 0)
        self.xGrid.addWidget(self.xMax, 2, 1)

        self.yMin = QtWidgets.QLineEdit()
        self.yMax = QtWidgets.QLineEdit()
        self.yGrid = QtWidgets.QGridLayout()
        self.yGrid.setSpacing(10)
        self.yGrid.addWidget(self.parameter, 1, 0)
        self.yGrid.addWidget(self.yMin, 2, 0)
        self.yGrid.addWidget(self.yMax, 2, 1)

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addStretch(1)

        self.hboxBtns = QtWidgets.QHBoxLayout()
        self.hboxBtns.addStretch(1)
        self.btnUpdate = IconButton(icons_location/'OK.png', self) 
        self.btnUpdate.clicked.connect(self.updateScale)     
        self.btnCancel = IconButton(icons_location/'Cancel.png', self)   

        self.btnCancel.clicked.connect(self.close)
        self.hboxBtns.addWidget(self.btnUpdate)
        self.hboxBtns.addWidget(self.btnCancel)

        self.fbox = QtWidgets.QFormLayout()
        self.fbox.addRow(self.xGrid)
        self.fbox.addRow(self.yGrid)
        self.fbox.addRow(self.hboxBtns)

        self.setLayout(self.fbox)
        self.setFocus()
        self.setWindowTitle("Scale Manager")
        self.setGeometry(300, 300, 300, 150)
        _center(self)
        self.setFocus()

        self.gwDict = {}
        for gwObject in self.gwObjects:
            self.gwDict[gwObject.par] = gwObject.yScale[:]

    def onChangeEvent(self):
        if self.yMin.text():
            self.gwDict[self.prevParVal][0] = int(str(self.yMin.text()))
        if self.yMax.text():
            self.gwDict[self.prevParVal][1] = int(str(self.yMax.text()))

        for i in self.par:
            if str(self.parameter.currentText()) == i:
                self.yMin.clear()
                self.yMin.setPlaceholderText(i+" min ("+str(self.gwDict[i][0])+")")
                self.yMax.clear()
                self.yMax.setPlaceholderText(i+" max ("+str(self.gwDict[i][1])+")")
                self.prevParVal = i

    def updateScale (self):
        """Change the values of the instance variables and specific graph widget plots
        after update button is clicked.
        """
        if self.xMin.text():
            self.xMinVal = int(str(self.xMin.text()))

        if self.xMax.text():
            self.xMaxVal = int(str(self.xMax.text()))

        if self.yMin.text():
            self.gwDict[self.prevParVal][0] = int(str(self.yMin.text()))

        if self.yMax.text():
            self.gwDict[self.prevParVal][1] = int(str(self.yMax.text()))

        for gwObject in self.gwObjects:
            gwObject.yScale = self.gwDict[gwObject.par][:]
            gwObject.xScale = [self.xMinVal, self.xMaxVal]
            gwObject.firstPlot()
        self.close()
        QtWidgets.QMessageBox.information(self, "Information", "Done!")
class IconButton(QtWidgets.QPushButton):
    def __init__(self,image_path, parent=None ):
        super(IconButton, self).__init__('', parent)
        self.setFixedSize(40, 40)
        self.setIcon(QtGui.QIcon(QtGui.QPixmap(str(image_path))))
        self.setFlat(True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.setIconSize(QtCore.QSize(40,40))
      
class PolyFitWindow(QtWidgets.QWidget):
    
    def __init__(self, par):
        super(PolyFitWindow, self).__init__()
        self.setProperty("popupBg", True)
        # Enable stylesheet background (needed for border-image on top-level QWidget)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.par = par
        polys = [1,2,3,4,5,6,7,8]
        self.minDegreeLabel = QtWidgets.QLabel("Min Degree of Polynomial")
        self.minDegree = QtWidgets.QComboBox()
        for degree in polys:
            self.minDegree.addItem(str(degree))
        self.minDegree.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.maxDegreeLabel = QtWidgets.QLabel("Max Degree of Polynomial")
        self.maxDegree = QtWidgets.QComboBox()
        for degree in polys[::-1]:
            self.maxDegree.addItem(str(degree))
        self.maxDegree.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.lowerBoundaryLabel = QtWidgets.QLabel("Lower Boundary Limit")
        self.lowerBoundary = QtWidgets.QLineEdit()
        self.upperBoundaryLabel = QtWidgets.QLabel("Upper Boundary Limit")
        self.upperBoundary = QtWidgets.QLineEdit()
        if self.par.split('_')[0] in ['VROT']:
            self.flatOuterRingsLabel = QtWidgets.QLabel("Number of Outer Flat Rings")
            self.flatOuterRings = QtWidgets.QLineEdit()
        else:
            self.innerFlatringsLabel = QtWidgets.QLabel("Inner Flat Rings")
            self.innerFlatrings = QtWidgets.QLineEdit()
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
        if self.par.split('_')[0] in ['VROT']:
            self.flatOuterRingsLabel = QtWidgets.QLabel("Number of Outer Flat Rings")
            self.flatOuterRings = QtWidgets.QLineEdit()
            self.grid.addWidget(self.flatOuterRingsLabel, 5, 0)
            self.grid.addWidget(self.flatOuterRings, 5, 1)
        else:
            self.innerFlatringsLabel = QtWidgets.QLabel("Inner Flat Rings")
            self.innerFlatrings = QtWidgets.QLineEdit()
            self.grid.addWidget(self.innerFlatringsLabel, 5, 0)
            self.grid.addWidget(self.innerFlatrings, 5, 1)

        self.btnOK = IconButton(icons_location/'OK.png', self)       
        self.btnCancel = IconButton(icons_location/'Cancel.png', self)   

        self.hbox = QtWidgets.QHBoxLayout()
        #self.hbox.addStretch(1)
        self.hbox.addWidget(self.btnOK)
        self.hbox.addWidget(self.btnCancel)

        self.grid.addLayout(self.hbox, 6, 0,1,2)

        if self.par.split('_')[0] in ['INCL','PA']:
            self.warped = QtWidgets.QCheckBox(text="Fit Angular Momentum Vector?")
            self.grid.addWidget(self.warped, 7, 0)
       


        self.setLayout(self.grid)

        self.setWindowTitle("Polynomial Fit Specification")
        self.setGeometry(300, 300, 300, 150)

        _center(self)
        self.setFocus()


class ParamSpec(QtWidgets.QWidget):

    def __init__(self, par, windowTitle,plotted_parameters = None, addLocation=False):
        super(ParamSpec, self).__init__()
        self.setProperty("popupBg", True)
        # Enable stylesheet background (needed for border-image on top-level QWidget)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.par = par

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
        self.uMeasLabel = QtWidgets.QLabel("Unit Measurement")
        self.unitMeasurement = QtWidgets.QLineEdit()
        # self.unitMeasurement.setPlaceholderText("Unit Measurement")
      
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)
        self.grid.addWidget(self.parameterLabel, 1, 0)
        self.grid.addWidget(self.parameter, 1, 1)
        self.grid.addWidget(self.uMeasLabel, 2, 0)
        self.grid.addWidget(self.unitMeasurement, 2, 1)
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
   
            self.grid.addWidget(self.afterLabel, 3, 0)
            self.grid.addWidget(self.afterParameter, 3, 1)
        
        self.btnOK = IconButton(icons_location/'OK.png', self)       
        self.btnCancel = IconButton(icons_location/'Cancel.png', self)   

        self.hbox = QtWidgets.QHBoxLayout()
        #self.hbox.addStretch(1)
        self.hbox.addWidget(self.btnOK)
        self.hbox.addWidget(self.btnCancel)

        self.grid.addLayout(self.hbox, 4 if addLocation else 3, 0,1,2)
        self.setLayout(self.grid)

        self.setWindowTitle(windowTitle)
        self.setGeometry(300, 300, 300, 150)

        _center(self)
        self.setFocus()


class MainWindow(QtWidgets.QMainWindow):
    runNo = 0
    key = "Yes"
    loops = 0
    ncols = 5; nrows = 5
    INSET = 'None'
    par = ['VROT', 'SBR', 'INCL', 'PA','SDIS','XPOS']
    tmpDeffile = os.getcwd() + "/tmpDeffile.def"
    progressPath = ''
    fileName = ""
    gwObjects = []
    t = 0
    scrollWidth = 0; scrollHeight = 0
    before = 0
    numPrecisionY = {}
    numPrecisionX = 0
    NUR = 0
    data = []
    parVals = {}
    parValsErr = {}
    historyList = {}
    xScale = [0, 0]
    yScale = {'VROT':[0, 0]}
    mPress = [-5]
    mRelease = ['None']
    mMotion = [-5]
    initial_size = 0.75

    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        # monitor-based sizing was commented out; default to fixed initial dimensions
        monitor = QtWidgets.QApplication.primaryScreen()
        monitor_size = monitor.size()
        self.initial_height = monitor_size.height() * self.initial_size
        self.initial_width = monitor_size.width() * self.initial_size
        #self.initial_height = 1024
        #self.initial_width = 1536
        
        self.resize(int(self.initial_width), int(self.initial_height))
        _center(self)
        QtCore.QTimer.singleShot(100, self.openDef)
    
    def initUI(self):
        #self.showMaximized()
        
        self.setWindowTitle('TiRiFiG')
        # define a widget sitting in the main window where all other widgets will live
        central_widget = QtWidgets.QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        # make this new widget have a vertical layout
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.setContentsMargins(0, 0, 0, 0)
        vertical_layout.setSpacing(0)
        central_widget.setLayout(vertical_layout)
        # add the buttons and the scroll area which will have the graph widgets
        # open button
        #btnOpen = QtWidgets.QPushButton('&Open File')
        #btnOpen.setFixedSize(80, 30)
        #btnOpen.setToolTip('Open .def file')
        #btnOpen.clicked.connect(self.openDef)
        #vertical_layout.addWidget(btnOpen)
        # scroll area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll_area.viewport().setAutoFillBackground(False)
        scroll_area.setViewportMargins(0, 0, 0, 0)
        # the scroll area needs a widget to be placed inside of it which will hold the content
        # create one and let it have a grid layout
        self.scroll_area_content = QtWidgets.QWidget()
        self.scroll_area_content.setContentsMargins(0, 0, 0, 0)
        self.scroll_area_content.setAutoFillBackground(False)
        self.scroll_grid_layout = QtWidgets.QGridLayout()
        self.scroll_grid_layout.setContentsMargins(0, 0, 0, 0)
        #vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_grid_layout.setSpacing(0)
        self.scroll_grid_layout.setHorizontalSpacing(0)
        self.scroll_grid_layout.setVerticalSpacing(0)
        
        self.scroll_area_content.setLayout(self.scroll_grid_layout)
        scroll_area.setWidget(self.scroll_area_content)
        vertical_layout.addWidget(scroll_area)
        self.createActions()
        self.createMenus()

    def createActions(self):
        self.exitAction = QtGui.QAction("&Exit", self)
        self.exitAction.setShortcut("Ctrl+Q")
        self.exitAction.setStatusTip('Leave the app')
        self.exitAction.triggered.connect(self.quitApp)

        self.openFile = QtGui.QAction("&Open File", self)
        self.openFile.setShortcut("Ctrl+O")
        self.openFile.setStatusTip('Load .def file to be plotted')
        self.openFile.triggered.connect(self.openDef)

        self.saveChanges = QtGui.QAction("&Save", self)
        self.saveChanges.setStatusTip('Save changes to .def file')
        self.saveChanges.triggered.connect(self.saveAll)

        self.saveAsFile = QtGui.QAction("&Save as...", self)
        self.saveAsFile.setStatusTip('Create another .def file with current '
                                     'paramater values')
        self.saveAsFile.triggered.connect(self.saveAsAll)

        self.undoAction = QtGui.QAction("&Undo", self)
        self.undoAction.setShortcut("Ctrl+Z")
        self.undoAction.setStatusTip('Undo last action')
        self.undoAction.triggered.connect(self.undoCommand)

        self.redoAction = QtGui.QAction("&Redo", self)
        self.redoAction.setShortcut("Ctrl+Y")
        self.redoAction.setStatusTip('Redo last action')
        self.redoAction.triggered.connect(self.redoCommand)

        self.openTextEditor = QtGui.QAction("&Open Text Editor...", self)
        self.openTextEditor.setStatusTip('View the current open .def file in '
                                         'preferred text editor')
        self.openTextEditor.triggered.connect(self.openEditor)

        self.startTF = QtGui.QAction("&Start TiriFiC", self)
        self.startTF.setStatusTip('Starts TiRiFiC from terminal')
        self.startTF.triggered.connect(self.startTiriFiC)

        self.winSpec = QtGui.QAction("&Window Specification", self)
        self.winSpec.setStatusTip('Determines the number of rows and columns in a plot')
        self.winSpec.triggered.connect(self.setRowCol)

        self.scaleMan = QtGui.QAction("&Scale Manager", self)
        self.scaleMan.setStatusTip('Manages behaviour of scale and min and max values')
        self.scaleMan.triggered.connect(self.SMobj)

        self.paraDef = QtGui.QAction("&Add Parameter", self)
        # self.paraDef.setStatusTip('Determines which parameter is plotted')
        self.paraDef.triggered.connect(self.add_parameter_dialog)

    def createMenus(self):
        mainMenu = self.menuBar()

        self.fileMenu = mainMenu.addMenu('&File')
        self.fileMenu.addAction(self.openFile)
        self.fileMenu.addAction(self.undoAction)
        self.fileMenu.addAction(self.redoAction)
        self.fileMenu.addAction(self.saveChanges)
        self.fileMenu.addAction(self.saveAsFile)
        self.fileMenu.addAction(self.exitAction)

        # editMenu = mainMenu.addMenu('&Edit')

        self.runMenu = mainMenu.addMenu('&Run')
        self.runMenu.addAction(self.openTextEditor)
        self.runMenu.addAction(self.startTF)

        self.paramMenu = mainMenu.addMenu('&Parameters')
        self.paramMenu.addAction(self.paraDef)
        
        self.prefMenu = mainMenu.addMenu('&Preferences')
        self.prefMenu.addAction(self.scaleMan)
        #self.prefMenu.addAction(self.paraDef)
        self.prefMenu.addAction(self.winSpec)

    def quitApp(self):
        if self.t != 0:
            self.t.cancel()
        QtWidgets.qApp.quit()

    def cleanUp(self):
        #This doesn't do anything at the moment
        # FIXME(Samuel 11-06-2018): Find a way to do this better

        self.key = "Yes"
        self.ncols = 5; self.nrows = 5
        self.INSET = 'None'
        self.par = ['VROT', 'SBR', 'INCL', 'PA','SDIS','XPOS']
        self.unitMeas = ['km/s', 'Jy km/s/sqarcs', 'degrees', 'degrees','km/s','degrees']
        # FIXME use Lib/tempfile.py to create temporary file
        self.tmpDeffile = os.getcwd() + "/tmpDeffile.def"
        self.fileName = ""
        self.gwObjects = []
        self.t = 0
        self.scrollWidth = 0; self.scrollHeight = 0
        self.before = 0
        self.numPrecisionY = {}
        self.numPrecisionX = 0
        self.NUR = 0
        self.data = []
        self.parVals = {}
        self.historyList = {}
        self.xScale = [0, 0]
        self.yScale = {'VROT':[0, 0]}
        self.mPress = [-5]
        self.mRelease = ['None']
        self.mMotion = [-5]

        self.initUI()

    def getData(self):
        """Loads data from specified .def file in open dialog box

        Keyword arguments:
        self-- this is the main window being displayed
            i.e. the current instance of the mainWindow class

        Returns:
        data:list
        The text found in each line of the opened file

        data will be a none type variable if the fileName is invalid or no file is chosen
        """

        # stores file path of .def to fileName variable after user selects file in open
        # dialog box
        # TODO (Samuel 28-11-2018): If cancel is selected then suppress the message in try/except below
        self.fileName, _filter = QtWidgets.QFileDialog.getOpenFileName(self, "Open .def File", "~/",
                                                                       ".def Files (*.def)")

        # assign texts of read lines to data variable if fileName is exists, else assign
        # None
        try:
            with open(self.fileName) as f:
                data = f.readlines()
        except:
            if self.fileName == '':
                pass
            else:
                QtWidgets.QMessageBox.information(self, "Information",
                                                  "Empty/Invalid file specified")
            return None
        else:
            return data

    def strType(self, var):
        """Determines the data type of a variable

        Keyword arguments:
        self-- main window being displayed i.e. the current instance of the mainWindow class
        var-- variable holding the values

        Returns:
        int, float or str : string

        The function evaluates the data type of the var object and returns int,
        float or str
        """
        # why are you putting this in a try block (fixme)
        try:
            if int(var) == float(var):
                return 'int'
        except:
            try:
                float(var)
                return 'float'
            except:
                return 'str'

    def numPrecision(self, data):
        """Determines and sets floating point precision

        Keyword arguments:
        self-- main window being displayed i.e. the current instance of the mainWindow
               class
        data (list)--  list of scientific values of type string
                       e.g. x = ["20.00E4","55.0003E-4",...]

        Returns:
        int

        Determines the highest floating point precision of data points
        """

        decPoints = []
        # ensure values from list to are converted string
        # FIX ME: Consider using enumerate instead of iterating with range and len
        for i in range(len(data)):
            data[i] = str(data[i])

        for i in range(len(data)):
            val = data[i].split(".")
        # check val has decimal & fractional part and append length of numbers of
        # fractional part
            if len(val) == 2:
                decPoints.append(len(val[1].split('E')[0]))

        # assign greatest precision in decPoints to class variables handling precision
        if len(decPoints) == 0:
            return 0
        else:
            return max(decPoints)

    def getParameter(self, data):
        """Fetches data points of specified parameter

        Keyword arguments:
        self-- main window being displayed i.e. the current instance of the
               mainWindow class
        data (list)--  list containing texts of each line loaded from .def file

        Returns:
        parVal:list
        The values appearing after the '=' symbol of the parameter specified in sKey.
        If search key isnt found, zero values are returned

        The data points for the specific parameter value are located and converted
        from string to float data types for plotting and other data manipulation
        """
        # search through fetched data for values of "PAR =" or "PAR = " or "PAR=" or
        # "PAR= "
        global fit_par

        # I need NUR value first that's why it's on a different loop
        for i in data:
            lineVals = i.split("=")
            if len(lineVals) > 1:
                lineVals[0] = ''.join(lineVals[0].split())
                if lineVals[0].upper() == "NUR":
                    parVal = lineVals[1].split()
                    self.NUR = int(parVal[0])
                    break
             
        for i in data:
            lineVals = i.split("=")
            if len(lineVals) > 1:
                lineVals[0] = ''.join(lineVals[0].split())
                parVal = lineVals[1].split()
              
              
                if lineVals[0].upper() == "INSET":
                    self.INSET = ''.join(lineVals[1].split())
                elif lineVals[0].upper() == "LOOPS":
                    self.loops = int(parVal[0])
                elif '_ERR' in lineVals[0].upper():
                    param_name = lineVals[0][1:].upper().replace('_ERR', '')
                    try:
                        self.parValsErr[param_name] = [float(Decimal(val)) for val in parVal]
                    except Exception as e:
                        logging.error(f"Error processing error values for {param_name}: {e}")
                else:
                    if (len(parVal) > 0 and not self.strType(parVal[0]) == 'str' and
                            not self.strType(parVal[-1]) == 'str' and
                            not self.strType(parVal[int(len(parVal) / 2)]) == 'str'):
                        if (len(parVal) == self.NUR or lineVals[0].upper() in
                                fit_par.keys()):
                            if lineVals[0].upper() == 'RADI':
                                self.numPrecisionX = self.numPrecision(parVal[:])
                            else:
                                self.numPrecisionY[str.upper(lineVals[0])] = (
                                    self.numPrecision(parVal[:]))
                            for i in range(len(parVal)):
                                parVal[i] = float(Decimal(parVal[i]))
                            self.parVals[str.upper(lineVals[0])] = parVal[:]
        for key in self.parVals:
            if key not in self.parValsErr:
                self.parValsErr[key] = [float('NaN')]*len(self.parVals[key])

    def openDef(self):
        """Opens data, gets parameter values, sets precision and sets scale

        Keyword arguments:
        self -- main window being displayed i.e. the current instance of the
                mainWindow class

        Returns:
        None

        Makes function calls to getData and getParameter functions, assigns
        values to dictionaries parVals and firstPlot historyList and defines
        the x-scale and y-scale for plotting on viewgraph
        """
        global fit_par
        data = self.getData()
        #self.getParameter(data)
        try:
            self.getParameter(data)
        except:
            if data is None:
                pass
            else:
                QtWidgets.QMessageBox.information(self, "Information",
                                                  "Tilted-ring parameters not retrieved")
                logging.info("The tilted-ring parameters could not be retrieved from the {}"
                             .format(self.fileName))
        else:
            self.data = data
            if self.runNo > 0:
                # FIXME reloading another file on already opened not properly working
                # user has to close open window and reopen file for such a case
                QtWidgets.QMessageBox.information(self, "Information",
                                                  "Close app and reopen to load file. Bug "
                                                  "being fixed")
                # self.cleanUp()
                # FIXME (Samuel 11-06-2018): Find a better way to do this
                # self.data = data
                # self.getParameter(self.data)
            else:
                # defining the x scale for plotting
                # this is the min/max + 10% of the difference between the min and max
                min_max_diff = max(self.parVals['RADI']) - min(self.parVals['RADI'])
                percentage_of_min_max_diff = 0.1 * min_max_diff
                lower_bound = min(self.parVals['RADI']) - percentage_of_min_max_diff
                upper_bound = max(self.parVals['RADI']) + percentage_of_min_max_diff
                self.xScale = [int(ceil(lower_bound)), int(ceil(upper_bound))]
                
                self.scrollWidth = self.scroll_area_content.width()
                self.scrollHeight = self.scroll_area_content.height()

                # make a dict to save the graph widgets to be plotted
                # note that this approach will require another loop.
                # Not ideal but it gets the job done for now.
                g_w_to_plot = {}
                # ensure there are the same points for parameters as there are for RADI as
                # specified in NUR parameter
                for key, val in self.parVals.items():
                    diff = self.NUR - len(val)
                    if key == 'RADI': #use this implementation in other diff checkers
                        if diff == self.NUR:
                            for j in np.arange(0.0, (int(diff) * 40.0), 40):
                                self.parVals[key].append(j)
                        elif diff > 0 and diff < self.NUR:
                            for j in range(int(diff)):
                                self.parVals[key].append(self.parVals[key][-1] + 40.0)
                        continue
                    else:
                        if diff == self.NUR:
                            for j in range(int(diff)):
                                self.parVals[key].append(0.0)
                        elif diff > 0 and diff < self.NUR:
                            for j in range(int(diff)):
                                self.parVals[key].append(val[-1])

                   
                    min_max_diff = max(self.parVals[key]) - min(self.parVals[key])
                    percentage_of_min_max_diff = 0.1 * min_max_diff
                    lower_bound = min(self.parVals[key]) - percentage_of_min_max_diff
                    upper_bound = max(self.parVals[key]) + percentage_of_min_max_diff
                    # are the min/max values the same
                    if np.subtract(max(self.parVals[key]), min(self.parVals[key])) == 0:
                        self.yScale[key] = [lower_bound/2, upper_bound*1.5]
                    else:
                        self.yScale[key] = [lower_bound, upper_bound]
                    
                    unit = fit_par[key] if key in fit_par.keys() else ""
                    # Do we really need to create all graph widgets here?
                    if key in self.par:
                        new_widget = self.create_new_widget(key,unit)
                        self.gwObjects.append(new_widget)
                        g_w_to_plot[key] = new_widget
                        del new_widget

                # retrieve the values in order and build a list of ordered key-value pairs
                ordered_dict_items = [(key, g_w_to_plot[key]) for key in self.par]
                for idx, items in enumerate(ordered_dict_items):
                    graph_widget = items[1] # what does 1 represent
                    self.scroll_grid_layout.addWidget(graph_widget, idx, 0)
                del g_w_to_plot, ordered_dict_items
                self.runNo+=1

    def undoCommand(self):
        global currPar
        for i in range(len(self.gwObjects)):
            if self.gwObjects[i].par == currPar:
                self.gwObjects[i].undoKey()
                break

    def redoCommand(self):
        global currPar
        for i in range(len(self.gwObjects)):
            if self.gwObjects[i].par == currPar:
                self.gwObjects[i].redoKey()
                break

    def setRowCol(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Window number Input Dialog",
                                                  "Specify the number of rows and columns (rows,columns):")
        if ok:
            if text:
                text = str(text)
                text = text.split(",")
                self.nrows = int(text[0])
                self.ncols = int(text[1])
                if (self.nrows * self.ncols) >= len(self.par):
                    # clear the existing graph objects
                    item_count = self.scroll_grid_layout.count()
                    for i in range(item_count):
                        widget_to_remove = self.scroll_grid_layout.itemAt(0).widget()
                        self.scroll_grid_layout.removeWidget(widget_to_remove)
                        widget_to_remove.close()

                    # get only the plot widgets for the we want to plot: defined in par
                    g_w_to_plot = [gwObject for gwObject in self.gwObjects
                                   if gwObject.par in self.par]
                    # retrieve the parameter for each graph widget in the g_w_to_plot list
                    # self.par for instance contains [VROT, SBR, PA and INCL]
                    # g_w_pars will also contain a list of parameters but in the order
                    # of self.gwObjects e.g. new_par = [PA, SBR, VROT, INCL].
                    # Create a new sorted list of graph widgets based as below:
                    # loop through self.par [VROT, SBR, PA, INCL]grab the index of the 
                    # parameter in the new_par list [PA, SBR, VROT, INCL] i.e. 
                    # index(VROT) in new_par list: 2
                    # index(SBR) in new_par list: 1
                    # index(PA) in new_par list: 0
                    # index(INCL) in new_par list: 3
                    # Use these indexes to get a sorted list of graph widgets
                    # from g_w_to_plot for the plotting
                    g_w_pars = [g_w.par for g_w in g_w_to_plot]
                    sorted_g_w_to_plot = []
                    for par in self.par:
                        idx = g_w_pars.index(par)
                        sorted_g_w_to_plot.append(g_w_to_plot[idx])
                    # delete the unordered list of graph widgets
                    del g_w_to_plot

                    counter = 0
                    for j in range(self.ncols):
                        for i in range(self.nrows): 
                            self.scroll_grid_layout.addWidget(
                                sorted_g_w_to_plot[counter], i, j)
                            # call the show method on the graphWidget object in order to
                            # display it
                            sorted_g_w_to_plot[counter].show()
                            # don't bother iterating to plot if all the parameters have been
                            # plotted else you'll get an error
                            if counter == len(sorted_g_w_to_plot) -1 :
                                break
                            counter += 1
                    for j in range(self.ncols):
                        self.scroll_grid_layout.setColumnStretch(j, 1)
                        self.scroll_grid_layout.setColumnMinimumWidth(j, 0)
                    for i in range(self.nrows):
                        self.scroll_grid_layout.setRowStretch(i, 1)
                    del sorted_g_w_to_plot
                else:
                    QtWidgets.QMessageBox.information(self, "Information",
                                                      "Product of rows and columns should"
                                                      " be at least the same as the current number of parameters"
                                                      " on viewgraph")

    def saveFile(self, newVals, sKey, unitMeasurement, numPrecisionX, numPrecisionY):
        """Save changes made to data points to .def file per specified parameter

        Keyword arguments:
        self--  main window being displayed i.e. the current instance of the
        mainWindow class
        newVals (list)-- list containing new values
        sKey (str)-- parameter search key

        Returns:
        None

        The .def file would be re-opened and updated per the new values that
        are contained in the parVal* variable
        """

        # get the new values and format it as e.g. [0 20 30 40 50...]
        txt = ""
        for i in range(len(newVals)):
            if sKey == 'RADI':
                txt = txt+" " +'{0:.{1}E}'.format(newVals[i], numPrecisionX)
            else:
                txt = txt+" " +'{0:.{1}E}'.format(newVals[i], numPrecisionY)

        # FIXME (11-06-2018) put this block of code in a try except block
        tmpFile = []
        with open(self.fileName, 'a') as f:
            status = False
            for i in self.data:
                lineVals = i.split("=")
                if len(lineVals) > 1:
                    lineVals[0] = ''.join(lineVals[0].split())
                    if sKey == lineVals[0]:
                        txt = "    "+sKey+"="+txt+"\n"
                        tmpFile.append(txt)
                        status = True
                    else:
                        tmpFile.append(i)
                else:
                    tmpFile.append(i)

            if not status:
                tmpFile.append("# "+sKey+" parameter in "+unitMeasurement+"\n")
                txt = "    "+sKey+"="+txt+"\n"
                tmpFile.append(txt)

            f.seek(0)
            f.truncate()
            for i in tmpFile:
                f.write(i)

            self.data = tmpFile[:]

    def saveAll(self):
        """Save changes made to data point to .def file for all parameters

        Keyword arguments:
        self -- main window being displayed i.e. the current instance of
        the mainWindow class

        Returns:
        None

        The saveFile function is called and updated with the current values being
        held by parameters.
        """
        for i in self.gwObjects:
            self.saveFile(i.parVals, i.par, i.unitMeas, i.numPrecisionX, i.numPrecisionY)

        self.saveMessage()

    def saveMessage(self):
        """Displays the information about save action

        Keyword arguments:
        self--  main window being displayed i.e. the current instance of the mainWindow class

        Returns:
        None

        Displays a messagebox that informs user that changes have been successfully
        written to the .def file
        """
        QtWidgets.QMessageBox.information(self, "Information",
                                          "Changes successfully written to file")

    def saveAs(self, fileName, newVals, sKey, unitMeasurement, numPrecisionX,
               numPrecisionY):
        """Creates a new .def file with current data points on viewgraph

        Keyword arguments:
        self--  main window being displayed i.e. the current instance of the
                mainWindow class
        fileName--  filePath where new file should be saved to
        newVals (list)--    list containing new values
        sKey (str)--    parameter search key

        Returns:
        None

        A new .def file would be created and placed in the specified file path
        """

        # get the new values and format it as [0 20 30 40 50...]
        txt = ""
        for i in range(len(newVals)):
            if sKey == 'RADI':
                txt = txt+" " +f'{newVals[i]:.{numPrecisionX}E}'
            else:
                txt = txt+" " +f'{newVals[i]:.{numPrecisionY}E}'

        tmpFile = []

        if not fileName == None:
            print(fileName)
            with open(fileName[0], 'a') as f:
                status = False
                for i in self.data:
                    lineVals = i.split("=")
                    if len(lineVals) > 1:
                        lineVals[0] = ''.join(lineVals[0].split())
                        if sKey == lineVals[0]:
                            txt = "    "+sKey+"="+txt+"\n"
                            tmpFile.append(txt)
                            status = True
                        else:
                            tmpFile.append(i)
                    else:
                        tmpFile.append(i)

                if not status:
                    tmpFile.append("# "+sKey+" parameter in "+unitMeasurement+"\n")
                    txt = "    "+sKey+"="+txt+"\n"
                    tmpFile.append(txt)

                f.seek(0)
                f.truncate()
                for i in tmpFile:
                    f.write(i)

                self.data = tmpFile[:]
                self.fileName = fileName

    def saveAsMessage(self):
        """Displays the information about save action

        Keyword arguments:
        self--  main window being displayed i.e. the current instance of the
                mainWindow class

        Returns:
        None

        Displays a messagebox that informs user that changes have been successfully
        written to the .def file
        """
        QtWidgets.QMessageBox.information(self, "Information", "File Successfully Saved")

    def saveAsAll(self):
        """Creates a new .def file for all parameters in current .def file opened

        Keyword arguments:
        self--  main window being displayed i.e. the current instance of
        the mainWindow class

        Returns:
        None

        The saveAs function is called and updated with the current values being
        held by parameters.
        """
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, "Save .def file as ",
                                                         os.getcwd(),
                                                         ".def Files (*.def)")
        for i in self.gwObjects:
            self.saveAs(fileName, i.parVals, i.par, i.unitMeas, i.numPrecisionX,
                        i.numPrecisionY)

        self.saveAsMessage()

    def slotChangeData(self, fileName):
        global fit_par
        with open(fileName) as f:
            self.data = f.readlines()

        self.getParameter(self.data)

        # counter = 0
        for i in fit_par.keys():
            for j in self.gwObjects:
                if j.par == i:
                    j.parVals = self.parVals[i][:]
                    j.parValRADI = self.parVals['RADI'][:]

        # FIXME(Samuel 11-06-2018):
        # the comments below will probably be important to keep/implement
        # it's possible that the user will delete some points in the .def file

        # ensure there are the same points for parameter as there are for RADI as
        # specified in NUR parameter
        # diff = self.NUR-len(self.parVals[self.par])
        # lastItemIndex = len(self.parVals[self.par])-1
        # if diff == self.NUR:
        #    for i in range(int(diff)):
        #        self.parVals[self.par].append(0.0)
        # elif diff > 0 and diff < self.NUR:
        #    for i in range(int(diff)):
        #        self.parVals[self.par].append(self.parVals[self.par][lastItemIndex])

        # defining the x and y scale for plotting
        if (np.subtract(max(self.gwObjects[0].parValRADI),
                        min(self.gwObjects[0].parValRADI)) == 0):
            self.xScale = [-100, 100]
        elif ((max(self.gwObjects[0].parValRADI) -
               min(self.gwObjects[0].parValRADI)) <= 100):
            self.xScale = [int(ceil(-2 * max(self.gwObjects[0].parValRADI))),
                           int(ceil(2 * max(self.gwObjects[0].parValRADI)))]
        else:
            self.xScale = [int(ceil(min(self.gwObjects[0].parValRADI) -
                                    0.1 * (max(self.gwObjects[0].parValRADI) -
                                           min(self.gwObjects[0].parValRADI)))),
                           int(ceil(max(self.gwObjects[0].parValRADI) +
                                    0.1 * (max(self.gwObjects[0].parValRADI) -
                                           min(self.gwObjects[0].parValRADI))))]

        for i in self.gwObjects:
            if not i.historyList[len(i.historyList)-1] == i.parVals[:]:
                i.historyList.append(i.parVals[:])

            i.xScale = self.xScale
            if np.subtract(max(i.parVals), min(i.parVals)) == 0:
                i.yScale = [-100, 100]
            elif (max(i.parVals)-min(i.parVals)) <= 100:
                i.yScale = [int(ceil(-2 * max(i.parVals))),
                            int(ceil(2 * max(i.parVals)))]
            else:
                i.yScale = [int(ceil(min(i.parVals) -
                                     0.1 * (max(i.parVals) - min(i.parVals)))),
                            int(ceil(max(i.parVals) + 0.1 * (max(i.parVals) -
                                                             min(i.parVals))))]
            i.firstPlot()

    def animate(self):
        if os.path.isfile(self.tmpDeffile):
            after = os.stat(self.tmpDeffile).st_mtime
            if self.before != after:
                self.before = after
                self.slotChangeData(self.tmpDeffile)

    def openEditor(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Text Editor Input Dialog",
                                                  "Enter text editor:")
        if ok:

            for i in self.gwObjects:
                self.saveAs(self.tmpDeffile, i.parVals, i.par, i.unitMeas,
                            i.numPrecisionX, i.numPrecisionY)

            if text:
                programName = str(text)
                try:
                    run([programName, self.tmpDeffile])
                except OSError:
                    QtWidgets.QMessageBox.information(self, "Information",
                                                      "{} is not installed or configured"
                                                      "properly on this system.".format(programName))
            else:
                # assign current modified time of temporary def file to before
                self.before = os.stat(self.tmpDeffile).st_mtime
                self.t = TimerThread(1, self.animate)
                self.t.start()

    def inProgress(self):
        """Displays the information about feature under development
        """
        QtWidgets.QMessageBox.information(self, "Information",
                                          "This feature is under development")

    def SMobj(self):
        self.sm = SMWindow(self.par, self.xScale, self.gwObjects)
        self.sm.show()
  
    def paramDef(self):
        global currPar, fit_par, selected_option
        user_input = self.ps.parameter.currentText().upper()
        unitMeas = str(self.ps.unitMeasurement.text())
        after_parameter = self.ps.afterParameter.currentText().upper()
        text_loc = ""
        if self.parameter_in_plot(user_input) or not self.parameter_in_data(user_input):
            return
        if after_parameter == "End":
            text_loc = "at the end of the current graph" 
        else:
            text_loc = f"after the parameter {after_parameter}"   
       
      
        # check if the inputted parameter value has its plot displayed
       
        print(f"We will add the parameter {user_input} {text_loc}")

        # the graph for the new tilted ring parameter will be inserted after the last plot
        # We could change this by adding a plot after option in the dialog box
        new_widget = self.obtain_widget_to_plot(user_input, unitMeas)

        #get the currently displayed widgets and their positions
        rows = []
        columns = [] 
        after_row = -1
        after_column = -1
        for i in range(self.scroll_grid_layout.count()):
            displayed = self.scroll_grid_layout.itemAt(i).widget()
            row_number, column_number = self.get_widget_location(displayed)
            if after_parameter != "End":
                if displayed.par == after_parameter:
                    after_row = row_number+1
                    after_column = column_number
            rows.append(row_number)
            columns.append(column_number)
        if after_row == -1:
            if after_parameter != "End":
                print(f"We could not find the parameter you specified to insert after. Adding at the end instead.")
            after_column = max(columns)
            column_index = [i for i,x in enumerate(columns) if x == after_column]
            after_row = max([rows[i] for i in column_index])+1
        if after_row >= self.nrows:
            after_column += 1
            if after_column == self.ncols:
                self.ncols += 1
            after_row = 0
        widgets_to_add = [{'widget': new_widget,
                          'row': after_row,
                          'column': after_column}]
        remove_start_index = -1
        for i in range(self.scroll_grid_layout.count()):
            displayed = self.scroll_grid_layout.itemAt(i).widget()
            row_number, column_number = self.get_widget_location(displayed)
            if column_number < after_column or (column_number == after_column and
                                     row_number < after_row):
                continue
            else:
                if remove_start_index == -1:
                    remove_start_index = i
                if row_number +1 < self.nrows:
                    row_number +=1                    
                else:
                    row_number = 0
                    column_number +=1
                    if column_number > self.ncols:
                        self.ncols += 1
                widgets_to_add.append({'widget': displayed,
                                       'row': row_number,
                                       'column': column_number})
        if remove_start_index  > -1:        
            for i in range(self.scroll_grid_layout.count()-1, remove_start_index-1, -1):
                widget_to_remove = self.scroll_grid_layout.itemAt(i).widget()
                self.scroll_grid_layout.removeWidget(widget_to_remove)
                widget_to_remove.hide()
                self.par.remove(widget_to_remove.par)
        for item in widgets_to_add:
            self.scroll_grid_layout.addWidget(item['widget'],
                                              item['row'],
                                              item['column'])
            item['widget'].show() 
            self.par.append(item['widget'].par)
        del widgets_to_add
        self.ps.close()

        return                  
      

    def create_new_widget(self, parameter,unit):
        new_gwObject = GraphWidget(self.xScale,
            self.yScale[parameter],
            unit,
            parameter,
            self.parVals[parameter],
            self.parValsErr[parameter],
            self.parVals['RADI'],
            "Yes",
            self.numPrecisionX,
            1,
            self.initial_width,
            self.initial_height)
        
        #new_gwObject.setMinimumSize(int(self.scrollWidth*3./4.),
        #    int(self.scrollHeight/2.))
        new_gwObject.setMinimumSize(750,500)
        #new_gwObject.setFixedSize(1050,500)
        #self.gwObjects[parIndex].btnAddParam.clicked.connect(
        #    self.gwObjects[parIndex].changeGlobal)
        #self.gwObjects[parIndex].btnAddParam.clicked.connect(
        #    self.insert_parameter_dialog)
        new_gwObject.btnEditParam.clicked.connect(
            new_gwObject.changeGlobal)
        new_gwObject.btnEditParam.clicked.connect(
            self.editParaObj)
        new_gwObject.btnCloseParam.clicked.connect(
            new_gwObject.changeGlobal)
        new_gwObject.btnCloseParam.clicked.connect(
            self.closeParaObj)         
                

        return new_gwObject
    
    def get_widget_location(self, widget):
        """Get the row and column of a widget in the grid layout.

        Keyword arguments:
        self -- main window being displayed i.e. the current instance of the
                mainWindow class
        widget -- the widget whose location is to be found

        Returns:
        row_number -- the row number of the widget
        column_number -- the column number of the widget
        """
        idx_in_layout = self.scroll_grid_layout.indexOf(widget)
        row_number, column_number, _rowSpan, _colSpan = self.scroll_grid_layout.getItemPosition(idx_in_layout)
        return row_number, column_number
        
    def parameter_in_plot(self,parameter):
       
        if parameter in self.par:
            QtWidgets.QMessageBox.information(self, "Information",
                f"The parameter {parameter} is already displayed")
            return True
        return False

    def parameter_in_data(self,parameter):       
        try:
            self.parVals[parameter]
        except KeyError:
            QtWidgets.QMessageBox.information(self, "Information",
                "This parameter is not defined in the .def file")
            return False
        return True
    
    def obtain_widget_to_plot(self, parameter, unitMeas): 
        list_of_t_r_p = [gwObject.par for gwObject in self.gwObjects]
        if unitMeas == "":
            #if the unit measure is blank, we attempt the default
            base_parameter = parameter.split('_')[0]
            if base_parameter in fit_par.keys():
                unitMeas = fit_par[base_parameter]
        else:
            #If the unit is not blank we want to update it in any existing graphs
            if parameter in list_of_t_r_p:
                for graph_widget in self.gwObjects:
                    if graph_widget.par == parameter:
                        graph_widget.unitMeas = unitMeas
                        break
        #If we do not have an existing graph we add one for the new parameter                         
        if parameter not in list_of_t_r_p:
            new_widget = self.create_new_widget(parameter,unitMeas)
            self.gwObjects.append(new_widget)
        else:
            new_widget = None
            for gw in self.gwObjects:
                if gw.par == parameter:
                    new_widget = gw
                    break
        return new_widget
  
                
    def editParamDef(self):
        global currPar, fit_par
          
        user_input = self.ps.parameter.currentText().upper()
        unitMeas = str(self.ps.unitMeasurement.text())
        
        if self.parameter_in_plot(user_input) or not self.parameter_in_data(user_input):
            return
        print(f'We will replace the parameter {currPar} with {user_input}')
        #select or create the widget to plot        
        new_widget = self.obtain_widget_to_plot(user_input, unitMeas)  
                             
        # Find the actual widget object for the current parameter in the layout
        old_widget = None
        for i,gw in enumerate(self.gwObjects):
            if gw.par == currPar:
                old_widget = gw
                break
        

        if old_widget is None:
            print("Could not find existing widget for currPar; aborting edit swap")
            return

        # Determine the position of the old widget in the grid
        row_number,column_number = self.get_widget_location(old_widget)

        # Remove old widget from layout and replace gwObjects entry
        self.scroll_grid_layout.removeWidget(old_widget)
        # Can't say I understand it but these seem to be required for 
        # a repetative add/remove to work properly
        old_widget.hide()
        new_widget.show()

        self.scroll_grid_layout.addWidget(new_widget, row_number, column_number)
        self.scroll_grid_layout.update()

        # Update current parameter to the new one       
        # update the parameter list
        self.par[self.par.index(currPar)] = user_input 
        currPar = user_input
        self.ps.close()
    
    def create_parameter_dialog(self, opt, title,add=False):
        global selected_option
        selected_option = opt
        val = []
        for i in self.parVals:
            if i in self.par:
                continue
            else:
                val.append(i)    
        self.ps = ParamSpec(val, title,plotted_parameters=self.par,addLocation=add)
        self.ps.show()
        self.ps.btnOK.clicked.connect(self.paramDef)
        self.ps.btnCancel.clicked.connect(self.ps.close)

    def add_parameter_dialog(self):
        selected_option = 'add'
        title = 'Add Parameter'
        self.create_parameter_dialog(selected_option, title,add=True)

    def insert_parameter_dialog(self):
        selected_option = 'insert'
        title = 'Insert Parameter'
        self.create_parameter_dialog(selected_option, title)

    def editParaObj(self):
        val = []
        for i in self.parVals:
            if i in self.par:
                continue
            else:
                val.append(i)

        self.ps = ParamSpec(val, "Edit Parameter")
        self.ps.show()
        self.ps.btnOK.clicked.connect(self.editParamDef)
        self.ps.btnCancel.clicked.connect(self.ps.close)

    def closeParaObj(self):
        #updated in changeGlobal
        global currPar
        print(f'Removing the Graph of parameter {currPar}')
        parIndex = [self.scroll_grid_layout.itemAt(i).widget().par 
            for i in range(self.scroll_grid_layout.count())].index(currPar)  
        widget_to_remove = self.scroll_grid_layout.itemAt(parIndex).widget()
        self.scroll_grid_layout.removeWidget(widget_to_remove)
        self.scroll_grid_layout.update()
        self.par.remove(currPar)
        widget_to_remove.close()
        
       
    def tirificMessage(self):
        """Displays the information about input data cube not available

        Keyword arguments:
        self--  main window being displayed i.e. the current instance of the
                mainWindow class

        Returns:
        None

        Displays a messagebox that informs user that changes have been successfully
        written to the .def file
        """
        QtWidgets.QMessageBox.information(self, "Information",
                                          "Data cube ("+self.INSET+") specified at INSET"
                                          " doesn't exist in specified directory.")

    def progressBar(self, cmd):
        progress = QtWidgets.QProgressDialog("Operation in progress...",
                                             "Cancel", 0, 100)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setMaximum(int(self.loops*1e6))
        progress.resize(500, 100)
        prev = 1
        message = "Stopped"
        completed = int(prev * 1e6) / 2
        status = 'running'
        progress.show()
        time.sleep(10)
        while cmd.poll() is None and status == 'running':
            with open(self.progressPath, 'r') as f:
                data = f.readlines()
                for i in data:
                    lin = i.split(" ")
                    if 'L:' in lin[0].upper():
                        count = lin[0].split(":")
                        count = count[1].split("/")
                        if int(count[0]) > prev:
                            if int(count[0]) == self.loops:
                                completed += 0.0001
                            else:
                                prev = int(count[0])
                                completed = prev * 1e6
                        else:
                            completed += 0.0001
                    elif "finish" in lin[0].lower():
                        status = 'finished'
                        progress.setValue(self.loops * 1e6)
                        message = i
                        break
            progress.setValue(completed)
            if progress.wasCanceled():
                cmd.kill()
                break
        progress.setValue(self.loops * 1e6)
        QtWidgets.QMessageBox.information(self, "Information", message)

    def startTiriFiC(self):
        """Start TiRiFiC

        Keyword arguments:
        self--  main window being displayed i.e. the current instance of
        the mainWindow class

        Returns:
        None

        Calls the os.system and opens terminal to start TiRiFiC
        """
        fitsfilePath = os.getcwd()
        fitsfilePath = fitsfilePath + "/" + self.INSET
        if os.path.isfile(fitsfilePath):
            for i in self.gwObjects:
                self.saveFile(
                    i.parVals, i.par, i.unitMeas, i.numPrecisionX, i.numPrecisionY)

            tmpFile = []
            with open(self.fileName, 'a') as f:
                for i in self.data:
                    lineVals = i.split("=")
                    if len(lineVals) > 1:
                        lineVals[0] = ''.join(lineVals[0].split())
                        if lineVals[0] == "ACTION":
                            tmpFile.append("ACTION = 1\n")
                        elif lineVals[0] == "PROMPT":
                            tmpFile.append("PROMPT = 0\n")
                        elif lineVals[0] == "GR_DEVICE":
                            tmpFile.append(i)
                            tmpFile.append("GR_CONT = \n")
                        elif lineVals[0] == "PROGRESSLOG":
                            tmpFile.append("PROGRESSLOG = progress\n")
                        elif lineVals[0] == "GR_CONT":
                            pass
                        else:
                            tmpFile.append(i)
                    else:
                        tmpFile.append(i)

                f.seek(0)
                f.truncate()
                for i in tmpFile:
                    f.write(i)
            try:
                cmd = run(["tirific", "deffile=", self.fileName])
            except OSError:
                QtWidgets.QMessageBox.information(self, "Information",
                                                  "TiRiFiC is not installed or configured"
                                                  " properly on system.")
            else:
                self.progressPath = str(self.fileName)
                self.progressPath = self.progressPath.split('/')
                self.progressPath[-1] = 'progress'
                self.progressPath = '/'.join(self.progressPath)
                self.progressBar(cmd)
        else:
            self.tirificMessage()

def logWarnings():
    # logging.captureWarnings(True)
    # logging.basicConfig(filename='test.log', format='%(asctime)s %(name)s %(levelname)s %(message)s',
    #                     datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logger = logging.getLogger(__name__)
    # warnings_logger = logging.getLogger("py.warnings")

    formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logger_file_handler = logging.FileHandler('TiRiFiG.log', mode='a')
    logger_file_handler.setFormatter(formatter)

    logger.addHandler(logger_file_handler)
    # warnings_logger.addHandler(logger_file_handler)
    # logger.setLevel(logging.DEBUG)
    # warnings_logger.setLevel(logging.DEBUG)

def main():
    logWarnings()
    if os.path.isfile(os.getcwd() + "/tmpDeffile.def"):
        os.remove(os.getcwd() + "/tmpDeffile.def")

    app = QtWidgets.QApplication(sys.argv)
    # Apply modern style (set a background image path if desired)
    background_image_path =  str(import_pack_files('TiRiFiG.utilities.background')/'Background.png')  # e.g., "path/to/your/image.png"
    try:
        apply_modern_style(app,background_image_path=background_image_path)
    except Exception as _e:
        # Non-fatal if styling fails
        pass
    GUI = MainWindow()
    GUI.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
