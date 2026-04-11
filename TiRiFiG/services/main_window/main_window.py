# -*- coding: UTF-8 -*-
#########################################################################################
# Author: Samuel (samueltwum1@gmail.com) with MSc supervisors                           #
# Copyright 2018 Samuel N. Twum                                                         #
#                                                                                       #
# GPL license - see LICENSE.txt for details                                             #
#########################################################################################

"""Main window implementation for TiRiFiG Qt6.

This module contains the application-level `MainWindow` controller and related
helpers used by the launcher entrypoint.
"""

# libraries
import os, logging,pickle
import warnings

os.environ["QT_API"] = "pyqt6"

# Suppress Qt painting-related warnings from matplotlib blitting
warnings.filterwarnings("ignore", message=".*Recursive repaint detected.*")
warnings.filterwarnings("ignore", message=".*Paint device returned engine.*")
warnings.filterwarnings("ignore", message=".*Painter not active.*")

from subprocess import Popen as run
from math import ceil
import numpy as np
import copy
import matplotlib
matplotlib.use("qt5agg")
from matplotlib import style
  
style.use("seaborn-v0_8")
from PyQt6 import QtCore, QtWidgets,QtGui
import pyFAT_astro.Support.support_functions as FAT_sup
from pyFAT_astro.Support.modify_template import update_disk_angles
from TiRiFiG.classes.classes import CustomMessageBox, TimerThread, _center
from TiRiFiG.services.parameter_trace.template_parameter_dialog_coordinator import TemplateParameterDialogCoordinator
from TiRiFiG.services.fitting.fitting_dialog import FittingFillDialog
from TiRiFiG.services.fitting.fitting_settings import FittingSettingsBootstrapService
from TiRiFiG.services.fitting.fitting_workflow_controller import FittingWorkflowController
from TiRiFiG.services.individual_graph.graph_widget_edit_dialog_service import GraphWidgetEditDialogService
from TiRiFiG.services.individual_graph.plot_parameter_workflow_controller import PlotParameterWorkflowController
from TiRiFiG.services.individual_graph.graph_widget_removal_service import GraphWidgetRemovalService
from TiRiFiG.services.individual_graph.scale_manager_window import SMWindow
from TiRiFiG.services.individual_graph.current_parameter_state import get_current_parameter
from TiRiFiG.services.tirific.open_def_service import OpenDefService
from TiRiFiG.services.tirific.save_all_service import SaveAllService
from TiRiFiG.services.main_window.set_row_col_service import SetRowColService
from TiRiFiG.services.main_window.slot_change_data_service import SlotChangeDataService
from TiRiFiG.services.tirific.tirific_editor_service import TirificEditorService
from TiRiFiG.services.parameter_trace.param_spec import ParamSpec
from TiRiFiG.services.tirific.tirific_run_service import TirificRunService
from TiRiFiG.utilities.parameters.deffile_parameters import DEFFILE_PARAMETERS
    
selected_option = None
fit_par = DEFFILE_PARAMETERS

class MainWindow(QtWidgets.QMainWindow):
    """Primary GUI controller for menu actions, plotting workflow, and I/O."""

    runNo = 0
    key = "Yes"
    ncols = 5; nrows = 5
    par = ['VROT', 'SBR', 'INCL', 'PA']
    tmpDeffile = os.getcwd() + "/tmpDeffile.def"
    progressPath = ''
    fileName = ""
    openedfileName = ""
    gwObjects = []
    t = 0
    scrollWidth = 0; scrollHeight = 0
    before = 0
    numPrecisionY = {}
    numPrecisionX = []
    NUR = 0
    data = []
    parVals = {}
    parValsErr = {}
    historyList = {}
    pyFAT_conf_file = None
    noise = 0.0
    beam = [0.0, 0.0, 0.0]
    channel_width = 0.0
    xScale = [0, 0]
    yScale = {'VROT':[0, 0]}
    mPress = [-5]
    mRelease = ['None']
    mMotion = [-5]
    initial_size = 0.75
    #Fitting keys
    fitting_parameters= ['VARY','VARINDX','PARMAX','PARMIN'
            ,'MODERATE','DELEND','DELSTART',
            'MINDELTA','SATDELT','ITESTART','ITEEND']

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

        self.plot_parameter = QtGui.QAction("&Add Parameter Plot", self)
        self.plot_parameter.setStatusTip('Add unplotted parameters to the graph')
        self.plot_parameter.triggered.connect(self.add_plot_parameter_dialog)

        self.paraDef = QtGui.QAction("&Add Parameter", self)
        self.paraDef.setStatusTip('Add a parameter to the def file.')
        self.paraDef.triggered.connect(self.add_parameter_dialog)
        
        self.modify_fit_settings = QtGui.QAction("&Modify Fit Settings", self)
        self.modify_fit_settings.setStatusTip('Modify fit settings for the def file.')
        self.modify_fit_settings.triggered.connect(self.modify_fit_settings_dialog)

        self.helpAction = QtGui.QAction("&Help", self)
        self.helpAction.setShortcut("F1")
        self.helpAction.setStatusTip('View help information about buttons and features')
        self.helpAction.triggered.connect(self.showHelp)

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
        self.paramMenu.addAction(self.plot_parameter)
        self.paramMenu.addAction(self.paraDef)
        self.paramMenu.addAction(self.modify_fit_settings)
        
        self.prefMenu = mainMenu.addMenu('&Preferences')
        self.prefMenu.addAction(self.scaleMan)
        #self.prefMenu.addAction(self.paraDef)
        self.prefMenu.addAction(self.winSpec)

        self.helpMenu = mainMenu.addMenu('&Help')
        self.helpMenu.addAction(self.helpAction)

    def quitApp(self):
        if self.t != 0:
            self.t.cancel()
        QtWidgets.qApp.quit()
    def setPFConfig(self):
        
        try:
            self.pyFAT_Configuration = pickle.load(self.pyFAT_config_file)    
        except Exception as e:
          
            self.pyFAT_Configuration = {'DEBUG': True,
                         'DEBUG_FUNCTION':'ALL',
                         'VERBOSE_LOG': False,
                         'VERBOSE_SCREEN': False,
                         'OUTPUTLOG': None,
                         'TIMING': False,
                         'NOISE': float(self.Tirific_Template['RMS']),
                         'BEAM': [float(self.Tirific_Template['BMAJ']), 
                                  float(self.Tirific_Template['BMIN']), 
                                  float(self.Tirific_Template['BPA'])],
                         'CHANNEL_WIDTH': 0.,
                         'NO_RINGS': self.NUR,
                         'LIMIT_MODIFIER': [1.0],
                         'LAST_RELIABLE_RINGS': [self.NUR,self.NUR],
                         'RC_UNRELIABLE': self.NUR,
                        }
          


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
        self.openedfileName = copy.deepcopy(self.fileName)  
        # assign texts of read lines to data variable if fileName is exists, else assign
        # None
       
        try:
            with open(self.fileName) as f:
                data = f.readlines()
        except:
            if self.fileName == '':
                pass
            else:
                CustomMessageBox.information(self, "Information",
                                                  "Empty/Invalid file specified")
            return None
        else:
            return data

  

    def numPrecision(self, string_value_line):
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
        #for i in range(len(data)):
        #    data[i] = str(data[i])
        values = string_value_line.split()
        for value in values:
            val = value.split(".")
            # check val has decimal & fractional part and append length of numbers of
            # fractional part
           
            if len(val) == 2:
                decPoints.append(len(val[1].split('E')[0]))
        if 'E' in value.upper():
            tpe = 'E'
        else:
            tpe = 'f'
        # assign greatest precision in decPoints to class variables handling precision
        if len(decPoints) == 0:
            return [0, tpe]
        else:
            return [max(decPoints), tpe]

    def getParameter(self):
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
        self.NUR = int(float(self.Tirific_Template['NUR']))
      
        for key in self.Tirific_Template:
            if len(self.Tirific_Template[key].split()) == self.NUR and\
                key not in self.fitting_parameters:
                if not '_ERR' in key:
                    if key == 'RADI':
                        self.parValsRADI = np.array([float(x) for x in self.Tirific_Template[key].split()], dtype=np.float64)
                        self.numPrecisionX = self.numPrecision(self.Tirific_Template[key])
                      
                    else:
                        print(f"Loading parameter values for {key}")
                        #print(self.Tirific_Template[key])
                        self.parVals[key] = np.array([float(x) for x in self.Tirific_Template[key].split()], dtype=np.float64)
                        self.numPrecisionY[key] = self.numPrecision(self.Tirific_Template[key])

                else:
                    param_name = key[1:].replace('_ERR', '').strip()
                    self.parValsErr[param_name] = np.array([float(x) for x in self.Tirific_Template[key].split()], dtype=np.float64)

      
       
            
       
        for key in self.parVals:
            if key not in self.parValsErr:
                self.parValsErr[key] = np.array([float('NaN')]*len(self.parVals[key]), dtype=np.float64)
    
    
    def set_fitting_dialog(self, *args, **kwargs):
        FittingSettingsBootstrapService.set_fitting_dialog(
            self,
            CustomMessageBox,
            FittingFillDialog,
            *args,
            **kwargs,
        )

    def getFittingSettings(self):
        """Fetch fitting settings from the loaded .def template."""
        FittingSettingsBootstrapService.get_fitting_settings(self)

    def setEmptyFittingValues(self, parameter):
        FittingSettingsBootstrapService.set_empty_fitting_values(self, parameter)

    def setRingFittingValues(self, fit_groups, varindex):
        FittingSettingsBootstrapService.set_ring_fitting_values(self, fit_groups, varindex)


    def obtain_varindx(self):
        return FittingSettingsBootstrapService.obtain_varindx(self)
       
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
        OpenDefService.open_def(
            self,
            CustomMessageBox,
            FAT_sup,
            QtCore,
            QtWidgets,
            np,
            set_plotScale,
            fit_par,
        )
        

    def undoCommand(self):
        current_parameter = get_current_parameter()
        for i in range(len(self.gwObjects)):
            if self.gwObjects[i].par == current_parameter:
                self.gwObjects[i].undoKey()
                break

    def redoCommand(self):
        current_parameter = get_current_parameter()
        for i in range(len(self.gwObjects)):
            if self.gwObjects[i].par == current_parameter:
                self.gwObjects[i].redoKey()
                break

    def setRowCol(self):
        SetRowColService.set_row_col(self, QtWidgets, CustomMessageBox)

    def saveParameter(self, newVals, newValsErr, sKey,
                 numPrecision):
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
        precision = f'.{numPrecision[0]}{numPrecision[1].lower()}'
        self.Tirific_Template[sKey] = ' '.join([f'{val:{precision}}' for val in newVals])
        if np.all(np.isnan(newValsErr)):
            pass
        else:
            self.Tirific_Template[f'# {sKey}_ERR'] = ' '.join([f'{val:{precision}}' for val in newValsErr])
        # update fitting settings in the template

    def check_fitting(self):
        FittingWorkflowController.check_fitting(self)
               
              
              
    def fill_fitting_values(self):
        FittingWorkflowController.fill_fitting_values(self)

    def show_group_fitting_menu(self, parameter, min_ring, max_ring):
        FittingWorkflowController.show_group_fitting_menu(
            self,
            parameter,
            min_ring,
            max_ring,
        )

    def edit_group_fitting(self, parameter, min_ring, max_ring):
        FittingWorkflowController.edit_group_fitting(
            self,
            parameter,
            min_ring,
            max_ring,
        )

    def fill_group_fitting_values(self):
        FittingWorkflowController.fill_group_fitting_values(self)

    def request_fitting_params(self, parameter):
        FittingWorkflowController.request_fitting_params(self, parameter)
       

    def updateFitSettings(self):
        FittingWorkflowController.update_fit_settings(self)

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
        SaveAllService.save_all(self, np)

    def write_tirific(self):
        angles = ['PA', 'INCL', 'PA_2', 'INCL_2']
        
        update_angle = True
        for angle in angles:
            if angle not in self.Tirific_Template:
                update_angle = False
                break
        if update_angle:
            update_disk_angles(self.pyFAT_Configuration,self.Tirific_Template)
        with open(self.fileName, 'w') as file:
            for key in self.Tirific_Template:
                if key[0:5] == 'EMPTY':
                    file.write('\n')
                else:
                    file.write((f"{key}= {self.Tirific_Template[key]} \n"))
    def saveMessage(self):
        """Displays the information about save action

        Keyword arguments:
        self--  main window being displayed i.e. the current instance of the mainWindow class

        Returns:
        None

        Displays a messagebox that informs user that changes have been successfully
        written to the .def file
        """
        CustomMessageBox.information(self, "Information",
                                          "Changes successfully written to file")

  

   

    def saveAsAll(self, name=None):
        """Creates a new .def file for all parameters in current .def file opened

        Keyword arguments:
        self--  main window being displayed i.e. the current instance of
        the mainWindow class

        Returns:
        None

        The saveAs function is called and updated with the current values being
        held by parameters.
        """
        if not name:
            fileName, _filter = QtWidgets.QFileDialog.getSaveFileName(self, "Save .def file as ",
                                                         os.getcwd(),
                                                         ".def Files (*.def)")
            if not fileName:  # User cancelled the dialog
                return
            self.fileName = fileName
        else:
            self.fileName = name
        self.openedfileName = self.fileName
        self.saveAll()

    def slotChangeData(self, fileName):
        SlotChangeDataService.slot_change_data(
            self,
            fileName,
            fit_par,
            np,
            ceil,
            set_plotScale,
        )

    def animate(self):
        if os.path.isfile(self.tmpDeffile):
            after = os.stat(self.tmpDeffile).st_mtime
            if self.before != after:
                self.before = after
                self.slotChangeData(self.tmpDeffile)

    def openEditor(self):
        TirificEditorService.open_editor(
            self,
            QtWidgets,
            run,
            CustomMessageBox,
            TimerThread,
        )

    def inProgress(self):
        """Displays the information about feature under development
        """
        CustomMessageBox.information(self, "Information",
                                          "This feature is under development")

    def showHelp(self):
        """Display help information about buttons, symbols, and rectangles"""
        help_text = """
<h2>TiRiFiG Help - Buttons, Symbols & Rectangles</h2>

<h3>Graph Buttons:</h3>
<ul>
<li><b>Group Select</b>: Select groups of rings to fit as a block. Click to toggle on/off. When active, draw rectangles around rings to group them.</li>
<li><b>Interpolate Rings</b>: Toggle interpolation mode. When active, click individual points to mark them for interpolation.</li>
<li><b>Fit On/Off</b>: Toggle fitting for selected rings. With three states: auto (gray), fit enabled (color), fit disabled.</li>
<li><b>Edit Parameter</b>: Edit the current parameter settings and unit measurements.</li>
<li><b>Close Parameter</b>: Remove the current parameter graph from the display.</li>
</ul>

<h3>Data Point Symbols:</h3>
<ul>
<li><b>● Green Circle</b> (FIT): Point is fitted and not interpolated</li>
<li><b>▼ Blue Triangle</b> (INT): Point is fitted but interpolated</li>
<li><b>✕ Red X</b> (NOFIT): Point is not fitted</li>
</ul>

<h3>Group Rectangles:</h3>
<ul>
<li><b>-- Dashed Lines</b>: Group is fitted as a block (BLOCK_FIT enabled)</li>
<li><b>: Dotted Lines</b>: Group is fitted individually (BLOCK_FIT disabled)</li>
<li>Rectangle color identifies the group - each unique group has a different color</li>
<li>Interior is transparent to see the data points clearly</li>
</ul>

<h3>Selecting and Managing Groups:</h3>
<ul>
<li>Click the Group Select button to enable group selection mode</li>
<li>Draw a rectangle around rings to group them together</li>
<li>If your selection overlaps an existing group:
  <ul>
  <li>Selected rings form a new group</li>
  <li>Non-selected rings from the old group form new separate groups</li>
  <li>Original BLOCK_FIT setting is preserved for non-selected groups</li>
  </ul>
</li>
<li>Click Group Select again to turn off selection mode</li>
</ul>
"""
        CustomMessageBox.information(self, "Help - TiRiFiG Guide", help_text)

    def SMobj(self):
        if not self.gwObjects:
            CustomMessageBox.information(self, "Information", "No plotted parameter available")
            return

        current_parameter = get_current_parameter()
        self.sm = SMWindow(self.gwObjects, current_parameter)
        self.sm.show()
  
    def paramDef(self):
        PlotParameterWorkflowController.param_def(self)

    def queueParamDef(self):
        PlotParameterWorkflowController.queue_param_def(self)

    def addQueuedParameters(self):
        PlotParameterWorkflowController.add_queued_parameters(self)

    def _insert_parameter_in_layout(self, user_input, unitMeas, after_parameter):
        PlotParameterWorkflowController.insert_parameter_in_layout(
            self,
            user_input,
            unitMeas,
            after_parameter,
        )
      

    def create_new_widget(self, parameter,unit):
        return PlotParameterWorkflowController.create_new_widget(self, parameter, unit)
    
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
        return PlotParameterWorkflowController.get_widget_location(self, widget)
        
    def parameter_in_plot(self,parameter):
        return PlotParameterWorkflowController.parameter_in_plot(self, parameter)

    def parameter_in_data(self,parameter):       
        return PlotParameterWorkflowController.parameter_in_data(self, parameter)
    
    def obtain_widget_to_plot(self, parameter, unitMeas): 
        return PlotParameterWorkflowController.obtain_widget_to_plot(self, parameter, unitMeas)
  
                
    def editParamDef(self):
        PlotParameterWorkflowController.edit_param_def(self)
    
    def create_parameter_dialog(self, opt, title,add=False):
        PlotParameterWorkflowController.create_parameter_dialog(self, opt, title, add=add)

    def add_plot_parameter_dialog(self):
        PlotParameterWorkflowController.add_plot_parameter_dialog(self)

    def add_parameter_dialog(self):
        selected_option = 'add'
        title = 'Add Parameter'
        self.add_parameter_to_def_dialog(selected_option, title,add=True)

    def _get_plot_dialog_coordinator(self):
        return PlotParameterWorkflowController.get_plot_dialog_coordinator(self)

    def _get_template_dialog_coordinator(self):
        """Return add-template-parameter dialog coordinator."""
        coordinator = getattr(self, "_template_dialog_coordinator", None)
        if coordinator is None:
            coordinator = TemplateParameterDialogCoordinator(
                self,
                fit_par,
                ParamSpec,
                CustomMessageBox,
            )
            self._template_dialog_coordinator = coordinator
        return coordinator

    def _get_graph_widget_factory(self):
        return PlotParameterWorkflowController.get_graph_widget_factory(self)

    def add_parameter_to_def_dialog(self, opt, title, add=True):
        """Dialog to add missing fit_par parameters into Tirific_Template."""
        del opt  # kept for compatibility with existing call signature
        self._get_template_dialog_coordinator().open_dialog(title, add=add)

    def modify_fit_settings_dialog(self):
        selected_option = 'add'
        title = 'Set Fitting Parameters'
        self.set_fitting_dialog(selected_option, title,add=False)

    def editParaObj(self):
        GraphWidgetEditDialogService.open_edit_dialog(self, ParamSpec)

    def closeParaObj(self):
        #updated in changeGlobal
        GraphWidgetRemovalService.remove_current_parameter_widget(
            self,
            get_current_parameter(),
        )
        
       
    def tirificMessage(self,message):
        """Displays the information about input data cube not available

        Keyword arguments:
        self--  main window being displayed i.e. the current instance of the
                mainWindow class

        Returns:
        None

        Displays a messagebox that informs user that changes have been successfully
        written to the .def file
        """
        return TirificRunService.show_run_warning(self, message, CustomMessageBox)

    def progressBar(self, cmd):
        TirificRunService.run_progress(self, cmd, CustomMessageBox)

    def startTiriFiC(self):
        """Start TiRiFiC

        Keyword arguments:
        self--  main window being displayed i.e. the current instance of
        the mainWindow class

        Returns:
        None

        Calls the os.system and opens terminal to start TiRiFiC
        """
        TirificRunService.start_run(self, run, CustomMessageBox)

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

def set_plotScale(values):
    min_max_diff = max(values) - min(values)
    percentage_of_min_max_diff = 0.1 * min_max_diff
    lower_bound = min(values) - percentage_of_min_max_diff
    upper_bound = max(values) + percentage_of_min_max_diff
    # are the min/max values the same
    if np.subtract(max(values), min(values)) == 0:
        scale = [lower_bound/2, upper_bound*1.5]
    else:
        scale = [lower_bound, upper_bound]
    return scale
