"""Individual graph widget implementation used by the Qt6 launcher."""

import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.widgets import RectangleSelector
from matplotlib.patches import Rectangle
from PyQt6 import QtCore, QtWidgets

from pyFAT_astro.Support.modify_template import fit_polynomial, determine_fit_order
from TiRiFiG.classes.classes import CustomMessageBox, CustomInputDialog, IconButton, icons_location
from TiRiFiG.services.individual_graph.current_parameter_state import set_current_parameter

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
    fitting_params_needed = QtCore.pyqtSignal(str)
    group_right_clicked = QtCore.pyqtSignal(str, int, int)

    def __init__(self, xScale, yScale, unitMeas, par, parVals,parValsErr, parValRADI,
            key, numPrecisionX, numPrecisionY,pyFAT_Configuration,Tirific_Template,
            paramenterFittingSetting, set_plot_scale_fn, polyfit_window_cls):
        super(GraphWidget, self).__init__()
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: transparent;")
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.xScale = xScale
        self.yScale = yScale
        self.pyFAT_Configuration = pyFAT_Configuration
        self.Tirific_Template = Tirific_Template
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
        self.parameterFitSetting = paramenterFittingSetting
        self.set_plot_scale = set_plot_scale_fn
        self.polyfit_window_cls = polyfit_window_cls
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
        self.line_connecting = None
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
        
        self.btnGroupSelect = IconButton(icons_location/'group.png', self, 
            start_grayscale=True,support_three_states=True, extra_icon_path=icons_location/'group_individual.png') 
        self.btnGroupSelect.clicked.connect(self.changeGlobal)
        self.btnGroupSelect.clicked.connect(self.selectGroups)
        self.group_selection_mode = 0
        self.rectangle_selector = None
        self.blue_selector = None
        self.green_selector = None
        

        self.btnInterRings = IconButton(icons_location/'interpolate.png', self, start_grayscale=True)
        self.btnInterRings.clicked.connect(self.changeGlobal)
        self.btnInterRings.clicked.connect(self.selectInterRings)
        self.interpolation_mode = False 

        self.btnFitOnOff = IconButton(icons_location/'fit_on.png', self, start_grayscale=True,
                        support_three_states=True, extra_icon_path=icons_location/'fit_off.png')   
        self.btnFitOnOff.clicked.connect(self.changeGlobal)
        self.btnFitOnOff.clicked.connect(self.toggleFitRings)
        self.fit_toggle_mode = 0     
        #self.btnEditParam.setToolTip('Modify plotted parameter')

        self.btnResetParam = IconButton(icons_location/'reset.png', self)
        self.btnCloseParam = IconButton(icons_location/'close.png', self)
        self.btnResetParam.setFixedSize(self.btnCloseParam.size())
        self.btnResetParam.setIconSize(self.btnCloseParam.iconSize())
        
        # FIX ME: use icon instead of text
        # self.btnEditParam.setIcon(QtGui.QIcon('utilities/icons/edit.png'))
        self.btnEditParam.setToolTip('Modify plotted parameter')
        self.btnFitPoly.setToolTip('Fit polynomial to data')
        self.btnGroupSelect.setToolTip('Select groups of rings to Fit')
        self.btnInterRings.setToolTip('Select rings to fit while interpolating over the rest')
        self.btnFitOnOff.setToolTip('Select or Toggle Fit Rings On/Off')
        self.btnResetParam.setToolTip('Reset points to original values')
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
        hbox.addWidget(self.btnFitOnOff)
        hbox.addStretch()
    
        hbox_right.addStretch()
        hbox_right.addWidget(self.btnResetParam)
        hbox_right.addWidget(self.btnCloseParam)
        grid.addLayout(hbox, 0, 0)
        grid.addLayout(hbox_right, 0, 1)
        grid.addWidget(self.canvas, 1, 0, 1, 2)

        self.firstPlot()

    def _find_group_at(self, xdata):
        """Return (min_ring, max_ring) for the group rectangle at data-x, or None."""
        if not self.parameterFitSetting.get('TO_FIT'):
            return None
        if len(self.parValRADI) < 2:
            return None
        ring_width = np.diff(self.parValRADI).max()
        groups_seen = {}
        for i in range(len(self.parValRADI)):
            ring_key = f"RING_{i+1}"
            if ring_key in self.parameterFitSetting:
                g = tuple(self.parameterFitSetting[ring_key]['GROUP'])
                if g not in groups_seen:
                    groups_seen[g] = True
        for group in groups_seen:
            min_ring, max_ring = group
            if min_ring == max_ring:
                continue
            min_radi = self.parValRADI[min_ring - 1] - ring_width * 0.5
            max_radi = self.parValRADI[max_ring - 1] + ring_width * 0.5
            if min_radi <= xdata <= max_radi:
                return (min_ring, max_ring)
        return None

    def reset_parameter_values(self):
        restored_values = copy.deepcopy(self.originalparVals)
        if np.array_equal(np.asarray(self.parVals), np.asarray(restored_values)):
            return
        self.redo = []
        self.parVals = restored_values
        if not np.array_equal(np.asarray(self.historyList[-1]), np.asarray(self.parVals)):
            self.historyList.append(copy.deepcopy(self.parVals))
        self.key = "Yes"
        self.plotFunc()

    def resizeEvent(self, event):
        """Update spacer widget width to 15% of cell width"""
        super().resizeEvent(event)
        if hasattr(self, 'spacer_widget'):
            self.spacer_widget.setFixedWidth(int(self.width() * 0.15))

    def smoothParameter(self):
        #First we get the desired input
        self.create_polyfit_dialog()

    def _set_mode_off(self, mode_attr, button_attr):
        """Reset a tri-state mode and button back to OFF state."""
        if getattr(self, mode_attr, 0) == 0:
            return
        setattr(self, mode_attr, 0)
        button = getattr(self, button_attr, None)
        if button is not None:
            button.set_state(0)

    def toggleFitRings(self):
        """Cycle through fit rings selection modes"""
        self.fit_toggle_mode = (self.fit_toggle_mode + 1) % 3
        self.btnFitOnOff.cycle_state()
        if self.fit_toggle_mode > 0:
            # Fit toggle and group selection share the rectangle selector; keep them exclusive.
            self._set_mode_off('group_selection_mode', 'btnGroupSelect')
        self.set_selector(mode = self.fit_toggle_mode)
        if self.fit_toggle_mode == 0:
            print(f"Fit rings mode OFF")
            self.rectangle_selector.set_active(False)
        elif self.fit_toggle_mode == 1:
            print(f"Fit rings mode: {self.fit_toggle_mode} - Fit selected rings only")
            self.parameterFitSetting['TO_FIT'] = True

            self.rectangle_selector.set_active(True)
        elif self.fit_toggle_mode == 2:
            print(f"Fit rings mode: {self.fit_toggle_mode} - Fit all except selected rings")
            self.rectangle_selector.set_active(True)

    def set_selector(self, mode):
        """Set up rectangle selectors for group selection modes"""
        if mode > 0:
            if self.rectangle_selector is None:
                self.rectangle_selector = RectangleSelector(
                    self.ax,
                    self._on_group_select,
                    useblit=True,
                    button=[1],
                    minspanx=5, minspany=5,
                    spancoords='pixels',
                    interactive=False,
                    props=dict(facecolor='cyan', edgecolor='blue', 
                          alpha=0.3, fill=True, linewidth=2)
                )
            self.rectangle_selector.set_active(True)      
        else:
            self.rectangle_selector.set_active(False)
                  
    def selectGroups(self):
        """Cycle through group selection modes"""
        self.group_selection_mode = (self.group_selection_mode + 1) % 3
        self.btnGroupSelect.cycle_state()
        if self.group_selection_mode > 0:
            # Group selection and fit toggle share the rectangle selector; keep them exclusive.
            self._set_mode_off('fit_toggle_mode', 'btnFitOnOff')
        self.set_selector(mode = self.group_selection_mode)
        if self.group_selection_mode > 0:
            if self.group_selection_mode == 1:
                print(f"Group selection mode: {self.group_selection_mode} - Set GROUP to be fitted as block")
            elif self.group_selection_mode == 2:
                print(f"Group selection mode: {self.group_selection_mode} - Set GROUP to be fitted as individual")
        else:
            # Disable rectangle selector
            print(f"Group selection mode OFF")

    def _break_overlapping_groups(self, selected_rings):
        """Break up any existing groups that overlap with the newly selected rings.
        
        When selecting rings that already belong to a group, this method dissolves
        that group and creates new groups from the remaining consecutive rings,
        while maintaining the original BLOCK_FIT setting.
        """
        groups_to_break = {}
        
        # Find all groups that overlap with selected rings
        for i in range(len(self.parValRADI)):
            ring_key = f"RING_{i+1}"
            if ring_key in self.parameterFitSetting:
                current_group = self.parameterFitSetting[ring_key]['GROUP']
                group_rings = set(range(current_group[0], current_group[1] + 1))
                selected_set = set(selected_rings)
                
                # If there's any overlap but not a complete match, mark group for breaking
                if group_rings & selected_set and group_rings != selected_set:
                    group_key = tuple(current_group)
                    if group_key not in groups_to_break:
                        # Capture the original BLOCK_FIT setting from the first ring in the group
                        original_block_fit = self.parameterFitSetting[ring_key]['BLOCK_FIT']
                        groups_to_break[group_key] = {
                            'all_rings': sorted(list(group_rings)),
                            'selected': sorted(list(group_rings & selected_set)),
                            'block_fit': original_block_fit
                        }
        
        # For each group to break, create new groups from remaining rings
        for group_key, info in groups_to_break.items():
            all_rings = info['all_rings']
            selected = set(info['selected'])
            remaining = [r for r in all_rings if r not in selected]
            original_block_fit = info['block_fit']
            
            if remaining:
                # Find consecutive sequences in remaining rings
                sequences = []
                current_seq = [remaining[0]]
                
                for ring in remaining[1:]:
                    if ring == current_seq[-1] + 1:
                        current_seq.append(ring)
                    else:
                        sequences.append(current_seq)
                        current_seq = [ring]
                sequences.append(current_seq)
                
                # Apply new groups to remaining rings, maintaining BLOCK_FIT setting
                for seq in sequences:
                    new_group = [seq[0], seq[-1]]
                    for ring in seq:
                        ring_key = f"RING_{ring}"
                        self.parameterFitSetting[ring_key]['GROUP'] = new_group
                        self.parameterFitSetting[ring_key]['BLOCK_FIT'] = original_block_fit
                    print(f"Rings {seq[0]}-{seq[-1]}: New group formed {new_group}")

    def _on_group_select(self, eclick, erelease):
        """Handle rectangle selection - update TO_FIT and INTERPOLATION for selected points"""
        try:
            # Get rectangle bounds
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata
            
            if x1 is None or x2 is None or y1 is None or y2 is None:
                return

            # Ensure x1 < x2 and y1 < y2
            x_min, x_max = min(x1, x2), max(x1, x2)
            y_min, y_max = min(y1, y2), max(y1, y2)
            
            # Find points within rectangle
            selected_count = 0
            rings = []
            for i, (x, y) in enumerate(zip(self.parValRADI, self.parVals)):
                if x_min <= x <= x_max and y_min <= y <= y_max:
                    rings.append(i+1)
                        
            if len(rings) > 0:
               

                if self.group_selection_mode > 0:                    
                    minring = min(rings)
                    maxring = max(rings)
                    
                    # Break up existing groups that overlap with the new selection
                    self._break_overlapping_groups(rings)
                    
                    # Apply the new group to selected rings
                    for ring in rings:
                        self.parameterFitSetting[f"RING_{ring}"]['GROUP'] = [minring, maxring]
                        if minring != maxring and self.group_selection_mode == 1:
                            self.parameterFitSetting[f"RING_{ring}"]['BLOCK_FIT'] = True
                        elif self.group_selection_mode == 2:
                            self.parameterFitSetting[f"RING_{ring}"]['BLOCK_FIT'] = False
                    # If any global fitting parameter is unset, request them now
                    fitmode_text = str(self.Tirific_Template.get('FITMODE', '0')).split()[0]
                    try:
                        fitmode_value = int(float(fitmode_text))
                    except Exception:
                        fitmode_value = 0
                    fitting_keys = ['PARMAX', 'PARMIN', 'MODERATE', 'DELEND', 'DELSTART',
                                    'MINDELTA', 'SATDELT', 'ITESTART', 'ITEEND']
                    if fitmode_value == 2:
                        fitting_keys = [k for k in fitting_keys if k not in ['SATDELT', 'ITESTART', 'ITEEND']]
                    if any(self.parameterFitSetting.get(k) is None for k in fitting_keys):
                        self.fitting_params_needed.emit(self.par)
                if self.fit_toggle_mode > 0:
                    #print(f'These {rings}')
                    for ring in rings:
                        if self.fit_toggle_mode == 1:
                            #print(f"Updated {len(rings)} ring(s): TO_FIT=True")
                            self.parameterFitSetting[f"RING_{ring}"]['TO_FIT'] = True
                        elif self.fit_toggle_mode == 2:
                            #print(f"Updated {len(rings)} ring(s): TO_FIT=True")
                            ring1,ring2 = self.parameterFitSetting[f"RING_{ring}"]['GROUP']
                            if ring1 != ring2 and  self.parameterFitSetting[f"RING_{ring}"]['BLOCK_FIT'] == True:
                                  CustomMessageBox.information(self, "Information",
                                    f"Cannot disable fitting of ring {ring} as it is part of a block fit group ({ring1}-{ring2}).\n"
                                    "Please modify the group first to disable block fitting.")
                            else:
                                self.parameterFitSetting[f"RING_{ring}"]['TO_FIT'] = False    
                # Update the plot to show new colors
                self.yScale = self.set_plot_scale(self.parVals)
                self.key = "Yes"
                self.plotFunc()
            else:
                print("No points selected in rectangle")
                
        except Exception as e:
            print(f"Error in group selection: {e}")
    
    def selectInterRings(self):
        """Toggle interpolation mode - when active, clicking points toggles INTERPOLATION"""
        self.interpolation_mode = not self.interpolation_mode
        self.btnInterRings.toggle_grayscale()
        
        if self.interpolation_mode:
            # Show status message
            print(f"Interpolation mode ON - click points to toggle INTERPOLATION status")
        else:
            print(f"Interpolation mode OFF")

    def fitPolynomial(self):
        def _lineedit_number(line_edit, default_value, as_int=False):
            raw_value = line_edit.text().strip()
            if raw_value == '':
                raw_value = line_edit.placeholderText().strip()
            if raw_value == '':
                return int(default_value) if as_int else float(default_value)
            try:
                numeric = float(raw_value)
            except Exception:
                numeric = float(default_value)
            return int(numeric) if as_int else numeric

        mindegree = int(float(self.inp.minDegree.currentText()))
        maxdegree = int(float(self.inp.maxDegree.currentText()))
        limits = [0., 0.]
        values = np.array(self.parVals,float)
        errors = np.array(self.parValsErr,float)
        radii = np.array(self.parValRADI,float)
        limits[0] = _lineedit_number(self.inp.lowerBoundary, float(np.nanmin(values)))
        limits[1] = _lineedit_number(self.inp.upperBoundary, float(np.nanmax(values)))
        key = self.par.split('_')[0]
        inner_flatrings = 4
        if key not in ['VROT']:
            inner_flatrings = _lineedit_number(self.inp.innerFlatrings, inner_flatrings, as_int=True)
     
        default_error = 0.1 * float(np.nanmean(values))
        replace_errors = _lineedit_number(self.inp.missing_error, default_error)
     
        errors = np.where(errors == 0, replace_errors, errors)   
        errors = np.where(np.isnan(errors), replace_errors, errors)   
        

        if key in ['INCL','PA']:
            if self.inp.warped.isChecked():
                #We have to fit the angular momentum function
                print(f'Not yet Working')
                return
        self.inp.close()
        zero_point = None
       
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

        self._fit_worker = FitWorker(self.pyFAT_Configuration, radii, 
            values, errors, key, self.par, self.Tirific_Template, 
            inner_flatrings, zero_point, limits, [mindegree, maxdegree])
        self._fit_worker.moveToThread(self._fit_thread)
        self._fit_thread.started.connect(self._fit_worker.run)

        def _done(fitted_values, final_poly):
            try:
                print(f'We fitted {self.par} with polynomial order {final_poly}')
                print(f'We got these values {fitted_values}')
                self.parVals = fitted_values
                self.yScale = self.set_plot_scale(fitted_values)
                self.key = "Yes"
                self.plotFunc()
            finally:
                if self._progress is not None:
                    self._progress.reset()
                    self._progress.hide()
                    self._progress = None

        def _error(msg: str):
            try:
                CustomMessageBox.critical(self, "Fit Error", msg)
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
        mean_val = float(np.nanmean(self.parVals)) 
        lower_bound = float(np.nanmin(self.parVals[1:]))
        upper_bound = float(np.nanmax(self.parVals))  
        st_fit,start_order,max_order,bound_fit = determine_fit_order(
            self.pyFAT_Configuration,self.par,  np.array(self.parValRADI,float)
            , np.array(self.parVals,float), 1)
        
        self.inp = self.polyfit_window_cls(self.par, yScale=self.yScale[:], 
            mean_val=mean_val, lower_boundary=lower_bound, 
            upper_boundary=upper_bound, max_order=max_order, min_order=start_order)
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
            was_visible = {}
            for state in self.states:
                was_visible[state] = self.line_current[state].get_visible()    
            was_connecting_visible = False
            for state in self.states:
                self.line_current[state].set_visible(False)
            if self.line_connecting is not None:
                was_connecting_visible = self.line_connecting.get_visible()
                self.line_connecting.set_visible(False)
            self.background = self.canvas.copy_from_bbox(self.ax.bbox)
            # Restore visibility
            for state in self.states:
                self.line_current[state].set_visible(was_visible[state])
            if self.line_connecting is not None:
                self.line_connecting.set_visible(was_connecting_visible)

            # Immediately re-blit the current line so it appears after full draws
            if self.line_connecting is not None:
                self.ax.draw_artist(self.line_connecting)
            for state in self.states:
                self.ax.draw_artist(self.line_current[state])
            self.canvas.blit(self.ax.bbox)
        else:
            # No animated line yet; just cache the background
            self.background = self.canvas.copy_from_bbox(self.ax.bbox)
      
        #self.background = self.canvas.copy_from_bbox(self.ax.bbox)

    def changeGlobal(self, val=None):
        if val == None:
            set_current_parameter(None)
        else:
            set_current_parameter(self.par)

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

       
        if event.dblclick and not event.xdata is None:
            # Handle double-click FIRST to prevent it from also triggering left-click logic
            self.mDblPress[0] = event.xdata
            self.mDblPress[1] = event.ydata
            
            text, ok = CustomInputDialog.getText(self, 'Input Dialog',
                                                  'Enter new node value:')
            if ok:
                if text:
                    newVal = float(str(text))
                    for j in range(len(self.parValRADI)):
                        if ((self.mDblPress[0] < (self.parValRADI[j])+3) and
                            (self.mDblPress[0] > (self.parValRADI[j])-3)):

                            self.parVals[j] = newVal
                            # Update internal data and trigger optimized redraw
                            self.yScale = self.set_plot_scale(self.parVals)
                            self.key = "Yes"
                            self.plotFunc()
                            break

                    # append the new point to the history if the last item in history differs
                    # from the new point
                    # Use numpy-safe equality check to avoid ambiguous truth value errors
                    try:
                        if not np.array_equal(np.asarray(self.historyList[-1]), np.asarray(self.parVals)):
                            # Preserve existing behaviour of copying current values
                            self.historyList.append(self.parVals[:])
                    except Exception:
                        # Fallback to list comparison if types are non-numpy
                        if not (self.historyList[-1] == self.parVals[:]):
                            self.historyList.append(self.parVals[:])

            self.mPress[0] = None
            self.mPress[1] = None
            return  # Exit early to prevent left-click handler from executing
        
        if event.button == 1 and not event.xdata is None:
            # Disable rectangle selector during interpolation mode
            if self.interpolation_mode and self.rectangle_selector is not None:
                self.rectangle_selector.set_active(False)
            
            # Check if we're in interpolation mode
           
            
        
            
            self.mPress[0] = event.xdata
            self.mPress[1] = event.ydata
            self.mRelease[0] = None
            self.mRelease[1] = None
            self.is_dragging = True
           
            if (self.fit_toggle_mode > 0 or self.group_selection_mode > 0):
                if self.rectangle_selector is not None:
                    self.rectangle_selector.set_active(True)
                return
             #No dragging when various modes are on
            if self.interpolation_mode:
                return
            # identify closest point to drag
            try:
                # Use vectorized NumPy operation instead of list comprehension
                distances = np.abs(np.array(self.parValRADI) - event.xdata)
                j = int(np.argmin(distances))
                # require it to be within a small x-threshold (similar to previous logic)
                if distances[j] <= 3:
                    self.drag_index = j
                else:
                    self.drag_index = None
            except Exception:
                self.drag_index = None

        if event.button == 3 and event.xdata is not None and not event.dblclick:
            group = self._find_group_at(event.xdata)
            if group is not None:
                self.group_right_clicked.emit(self.par, group[0], group[1])

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


                # Toggle INTERPOLATION for the clicked point
        if self.interpolation_mode or self.fit_toggle_mode > 0:        
            try:
                mouse_change = [0.,0.]
                for i in [0,1]:
                    mouse_change[i] = abs(self.mRelease[i] - self.mPress[i])
                if mouse_change[0] > 0.1 or mouse_change[1] > 0.1:
                    # Significant mouse movement - not a click
                    pass
                else:
                    # Use vectorized NumPy operation instead of list comprehension
                    distances = np.abs(np.array(self.parValRADI) - event.xdata)
                    j = int(np.argmin(distances))
                    if distances[j] <= 3:
                        # Toggle interpolation for this ring
                        ring_key = f"RING_{j+1}"
                        
                        
                        if self.interpolation_mode: 
                            current_interp = self.parameterFitSetting[ring_key]['INTERPOLATION']
                            self.parameterFitSetting[ring_key]['INTERPOLATION'] = not current_interp
                        elif self.fit_toggle_mode == 1:
                            self.parameterFitSetting[ring_key]['TO_FIT'] = True
                        elif self.fit_toggle_mode == 2:
                            ring1,ring2 = self.parameterFitSetting[ring_key]['GROUP']
                            if ring1 != ring2 and  self.parameterFitSetting[ring_key]['BLOCK_FIT'] == True:
                                CustomMessageBox.information(self, "Information",
                                    f"Cannot disable fitting of ring {j+1} as it is part of a block fit group.\n"
                                    "Please modify the group first to disable block fitting.")
                                return     
                            self.parameterFitSetting[ring_key]['TO_FIT'] = False
                        self.key = "Yes"
                        self.yScale = self.set_plot_scale(self.parVals)
                        self.plotFunc()
            except Exception as e:
                print(f"Error processeing click in current mode: {e}")
       


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
        
                bottom,top = self.ax.get_ylim()
                plotrange = top - bottom
                if abs(top-self.last_value) < abs(bottom - self.last_value):
                    self.last_value += 0.1 * abs(plotrange)
                else:
                    self.last_value -= 0.1 * abs(plotrange)
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

    def _draw_group_rectangles(self):
        """Draw dashed rectangles for each unique group with different colors"""
        
        # Define colors for different groups
        group_colors = [
            '#FF6B6B',  # Red
            '#4ECDC4',  # Teal
            '#45B7D1',  # Blue
            '#FFA07A',  # Light Salmon
            '#98D8C8',  # Mint
            '#F7DC6F',  # Yellow
            '#BB8FCE',  # Purple
            '#85C1E2',  # Light Blue
        ]
        
        # Track unique groups and their colors
        groups_seen = {}
        group_color_map = {}
        color_index = 0
        
        # Find all unique groups
        for i in range(len(self.parValRADI)):
            ring_key = f"RING_{i+1}"
            if ring_key in self.parameterFitSetting:
                group = tuple(self.parameterFitSetting[ring_key]['GROUP'])
                if group not in groups_seen:
                    groups_seen[group] = True
                    group_color_map[group] = group_colors[color_index % len(group_colors)]
                    color_index += 1
        ring_width = np.diff(self.parValRADI).max()
        # Draw rectangles for each unique group
        for group, color in group_color_map.items():
            if group[0] == group[1]:  # Skip single-ring groups (no need for rectangle)
                continue
                
            min_ring, max_ring = group
            
            # Find RADI values for min and max rings
            min_radi = self.parValRADI[min_ring - 1]-ring_width*0.5
            max_radi = self.parValRADI[max_ring - 1]+ring_width*0.5
            
            # Get y-axis limits
            if np.isnan(self.parValsErr).any():
                # If there are NaNs in parValsErr, just use parVals
                y_min = np.nanmin(self.parVals[min_ring-1:max_ring])
                y_max = np.nanmax(self.parVals[min_ring-1:max_ring])
            else:
                # Use parVals +/- parValsErr for y-limits
                y_min = np.nanmin(self.parVals[min_ring-1:max_ring] - self.parValsErr[min_ring-1:max_ring])
                y_max = np.nanmax(self.parVals[min_ring-1:max_ring] + self.parValsErr[min_ring-1:max_ring])
            y_min *= 0.95  # Add 5% padding below
            y_max *= 1.05  # Add 5% padding above
            y_range = y_max - y_min
            while y_range < 0.1 * np.nanmean(self.parVals):
                y_min -= 0.05 * np.nanmean(self.parVals)
                y_max += 0.05 * np.nanmean(self.parVals)
                y_range = y_max - y_min
            # Add some padding to height
            rect_y_min = y_min 
            rect_height = y_range 
            
            # Create rectangle with dashed or dotted lines based on BLOCK_FIT status
            rect_width = max_radi- min_radi
            
            # Check if this group is a block fit or individual fit
            # Get the first ring in the group to check BLOCK_FIT status
            first_ring_key = f"RING_{min_ring}"
            block_fit = self.parameterFitSetting[first_ring_key]['BLOCK_FIT']
            line_style = '--' if block_fit else ':'  # Dashed for block fit, dotted for individual
            
            rect = Rectangle(
                (min_radi, rect_y_min),
                rect_width,
                rect_height,
                linewidth=2,
                edgecolor=color,
                facecolor='none',
                linestyle=line_style,
                zorder=1
            )
            self.ax.add_patch(rect)

    def _get_points(self):
        """Get colors for each point based on TO_FIT and INTERPOLATION status.
        
        Returns:
            list: Color for each point ('red', 'blue', or 'green')
        """
        points_to_set = {'FIT': {'RADI': [], 'VALS': []},
            'INT': {'RADI': [], 'VALS': []},
            'NOFIT': {'RADI': [], 'VALS': []}}
       
       
        if not self.parameterFitSetting['TO_FIT']:
            points_to_set['NOFIT']['RADI'] = self.parValRADI[:]
            points_to_set['NOFIT']['VALS'] = self.parVals[:]
        else:
            for i in range(len(self.parVals)):
                ring_key = f"RING_{i+1}"     
                if not self.parameterFitSetting[ring_key]['TO_FIT']:
                        # Red: not fitted
                    points_to_set['NOFIT']['RADI'].append(self.parValRADI[i])
                    points_to_set['NOFIT']['VALS'].append(self.parVals[i])
                elif self.parameterFitSetting[ring_key]['INTERPOLATION']:
                        # Blue: fitted but interpolated
                    points_to_set['INT']['RADI'].append(self.parValRADI[i])
                    points_to_set['INT']['VALS'].append(self.parVals[i])
                else:
                        # Green: fitted and not interpolated
                    points_to_set['FIT']['RADI'].append(self.parValRADI[i])
                    points_to_set['FIT']['VALS'].append(self.parVals[i])
        
        return points_to_set

    def showInformation(self):
        """Show the information message

        Keyword arguments:
        self --         main window being displayed i.e. the current instance of the
        mainWindow class

        Returns:
        None

        Displays a messagebox that informs user there's no previous action to be undone
        """
        CustomMessageBox.information(self, "Information", "History list is exhausted")


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
        # Get colors for each point based on fitting status
        points_to_set = self._get_points()
        self.states = ['FIT','INT','NOFIT']
        colors = ['mediumseagreen','violet','red']
        markers = ['o','v','X']
        self.line_current = {}
        # Use scatter plot for individual point colors
        for state in self.states:
            self.line_current[state] = self.ax.scatter(points_to_set[state]['RADI'], 
                                                points_to_set[state]['VALS'], 
                                           c=colors[self.states.index(state)], 
                                           marker=markers[self.states.index(state)], s=50, zorder=4, 
                                          animated=True, edgecolors='black', linewidths=0.5)
        
        
        # Add connecting lines in grey
        self.line_connecting, = self.ax.plot(self.parValRADI, self.parVals, '--', 
                                            color='mediumseagreen', alpha=1., zorder=3, 
                                            animated=True, linewidth=1)
   
       
        self.ax.plot(self.parValRADI, self.originalparVals, '--ro', alpha=0.2, zorder=2)
        self.ax.errorbar(
                self.parValRADI,
                self.originalparVals,
                yerr=self.parValsErr,
                c='r', linestyle='-', alpha=0.2, zorder=2
            )
        
        # Draw group rectangles
        self._draw_group_rectangles()
       
        self.ax.set_xticks(self.parValRADI)
        #Make sure to catch the current line in the limits
        if self.line_current is not None:
            for state in self.states:
                self.line_current[state].set_visible(True)
            if self.line_connecting is not None:
                self.line_connecting.set_visible(True)
            self.canvas.draw()
        ylimits = self.ax.get_ylim()
        # Hide the animated line before the full draw to keep background clean
        if self.line_current is not None:
            for state in self.states:
                self.line_current[state].set_visible(False)
            if self.line_connecting is not None:
                self.line_connecting.set_visible(False)
        # Full draw for non-animated artists (axes, error bars, originals)
        self.ax.set_ylim(ylimits[0], ylimits[1])
        self.canvas.draw()
        # Cache clean background and then re-blit the current line
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        #if self.line_current is not None:
        for state in self.states:
            self.line_current[state].set_visible(True)
        if self.line_connecting is not None:
            self.line_connecting.set_visible(True)
        if self.line_connecting is not None:
            self.ax.draw_artist(self.line_connecting)
        for state in self.states:
            self.ax.draw_artist(self.line_current[state])
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
                    # Update scatter plot offsets
                    points_to_set = self._get_points()
                    for state in self.states: 
                        if len(points_to_set[state]['RADI']) > 0: 
                            offsets = list(zip(points_to_set[state]['RADI'], points_to_set[state]['VALS']))
                            self.line_current[state].set_offsets(offsets)
                  
                    # Update connecting line
                    if self.line_connecting is not None:
                        self.line_connecting.set_ydata(self.parVals)

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
                            if self.line_connecting is not None:
                                self.ax.draw_artist(self.line_connecting)
                            for state in self.states:      
                                self.ax.draw_artist(self.line_current[state])

                          
                            self.canvas.blit(self.ax.bbox)
                            self.canvas.flush_events()
                        else:
                            self.canvas.draw_idle()
                    self.key = "No"
        self.check_parameter_limits()

    def check_parameter_limits(self):
        """Check if the parameter plot limits exceed the parmin and parmax values."""
        if self.parameterFitSetting['PARMIN'] is None\
            or self.parameterFitSetting['PARMIN'] > self.yScale[0]:
            self.parameterFitSetting['PARMIN'] = self.yScale[0]
        if self.parameterFitSetting['PARMAX'] is None\
             or self.yScale[1] > self.parameterFitSetting['PARMAX']:
            self.parameterFitSetting['PARMAX'] = self.yScale[1]
        
     


            # If not dragging, do nothing heavy here
