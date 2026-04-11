"""Controller for plot-parameter dialog and widget workflow operations."""

import numpy as np

from TiRiFiG.classes.classes import CustomMessageBox
from TiRiFiG.services.individual_graph.plot_parameter_dialog_coordinator import PlotParameterDialogCoordinator
from TiRiFiG.services.individual_graph.current_parameter_state import get_current_parameter, set_current_parameter
from TiRiFiG.services.individual_graph.graph_widget import GraphWidget as IndividualGraphWidget
from TiRiFiG.services.parameter_trace.param_spec import ParamSpec
from TiRiFiG.services.polynomial_fitting.polyfit_window import PolyFitWindow
from TiRiFiG.utilities.parameters.deffile_parameters import DEFFILE_PARAMETERS


selected_option = None
fit_par = DEFFILE_PARAMETERS


class PlotParameterWorkflowController:
    """Encapsulate MainWindow plot-parameter add/edit workflow behavior."""

    class _InlineGraphWidgetFactory:
        def __init__(self, owner):
            self.owner = owner

        def create_widget(self, parameter, unit):
            return PlotParameterWorkflowController._build_graph_widget(self.owner, parameter, unit)

    @staticmethod
    def _set_plot_scale(values):
        min_max_diff = max(values) - min(values)
        percentage_of_min_max_diff = 0.1 * min_max_diff
        lower_bound = min(values) - percentage_of_min_max_diff
        upper_bound = max(values) + percentage_of_min_max_diff
        if np.subtract(max(values), min(values)) == 0:
            return [lower_bound / 2, upper_bound * 1.5]
        return [lower_bound, upper_bound]

    @staticmethod
    def param_def(owner):
        user_input = owner.ps.parameter.currentText().upper()
        unitMeas = str(owner.ps.unitMeasurement.text())
        after_parameter = owner.ps.afterParameter.currentText().upper()
        if PlotParameterWorkflowController.parameter_in_plot(owner, user_input) or not PlotParameterWorkflowController.parameter_in_data(owner, user_input):
            return
        PlotParameterWorkflowController.insert_parameter_in_layout(owner, user_input, unitMeas, after_parameter)
        owner.ps.close()

    @staticmethod
    def queue_param_def(owner):
        PlotParameterWorkflowController.get_plot_dialog_coordinator(owner).queue_current_parameter()

    @staticmethod
    def add_queued_parameters(owner):
        PlotParameterWorkflowController.get_plot_dialog_coordinator(owner).add_queued_parameters()

    @staticmethod
    def insert_parameter_in_layout(owner, user_input, unitMeas, after_parameter):
        after_upper = str(after_parameter).upper()
        if after_upper == "END":
            text_loc = "at the end of the current graph"
        else:
            text_loc = f"after the parameter {after_parameter}"
        print(f"We will add the parameter {user_input} {text_loc}")

        new_widget = PlotParameterWorkflowController.obtain_widget_to_plot(owner, user_input, unitMeas)

        after_upper = str(after_parameter).upper()
        rows = []
        columns = []
        after_row = -1
        after_column = -1
        for i in range(owner.scroll_grid_layout.count()):
            displayed = owner.scroll_grid_layout.itemAt(i).widget()
            row_number, column_number = PlotParameterWorkflowController.get_widget_location(owner, displayed)
            if after_upper != "END" and displayed.par == after_upper:
                after_row = row_number + 1
                after_column = column_number
            rows.append(row_number)
            columns.append(column_number)

        if after_row == -1:
            if after_upper != "END":
                print("We could not find the parameter you specified to insert after. Adding at the end instead.")
            try:
                after_column = max(columns)
                column_index = [i for i, x in enumerate(columns) if x == after_column]
                after_row = max([rows[i] for i in column_index]) + 1
            except ValueError:
                after_column = 0
                after_row = 0

        if after_row >= owner.nrows:
            after_column += 1
            if after_column == owner.ncols:
                owner.ncols += 1
            after_row = 0

        widgets_to_add = [{"widget": new_widget, "row": after_row, "column": after_column}]
        remove_start_index = -1
        for i in range(owner.scroll_grid_layout.count()):
            displayed = owner.scroll_grid_layout.itemAt(i).widget()
            row_number, column_number = PlotParameterWorkflowController.get_widget_location(owner, displayed)
            if column_number < after_column or (column_number == after_column and row_number < after_row):
                continue
            if remove_start_index == -1:
                remove_start_index = i
            if row_number + 1 < owner.nrows:
                row_number += 1
            else:
                row_number = 0
                column_number += 1
                if column_number > owner.ncols:
                    owner.ncols += 1
            widgets_to_add.append({"widget": displayed, "row": row_number, "column": column_number})

        if remove_start_index > -1:
            for i in range(owner.scroll_grid_layout.count() - 1, remove_start_index - 1, -1):
                widget_to_remove = owner.scroll_grid_layout.itemAt(i).widget()
                owner.scroll_grid_layout.removeWidget(widget_to_remove)
                widget_to_remove.hide()
                owner.par.remove(widget_to_remove.par)

        for item in widgets_to_add:
            owner.scroll_grid_layout.addWidget(item["widget"], item["row"], item["column"])
            item["widget"].show()
            owner.par.append(item["widget"].par)

    @staticmethod
    def create_new_widget(owner, parameter, unit):
        return PlotParameterWorkflowController.get_graph_widget_factory(owner).create_widget(parameter, unit)

    @staticmethod
    def get_widget_location(owner, widget):
        idx_in_layout = owner.scroll_grid_layout.indexOf(widget)
        row_number, column_number, _row_span, _col_span = owner.scroll_grid_layout.getItemPosition(idx_in_layout)
        return row_number, column_number

    @staticmethod
    def parameter_in_plot(owner, parameter):
        if parameter in owner.par:
            CustomMessageBox.information(
                owner,
                "Information",
                f"The parameter {parameter} is already displayed",
            )
            return True
        return False

    @staticmethod
    def parameter_in_data(owner, parameter):
        try:
            owner.parVals[parameter]
        except KeyError:
            CustomMessageBox.information(
                owner,
                "Information",
                "This parameter is not defined in the .def file",
            )
            return False
        return True

    @staticmethod
    def obtain_widget_to_plot(owner, parameter, unitMeas):
        list_of_t_r_p = [gw_object.par for gw_object in owner.gwObjects]

        if unitMeas == "":
            base_parameter = parameter.split("_")[0]
            if base_parameter in fit_par.keys():
                unitMeas = fit_par[base_parameter]["unit"]
        elif parameter in list_of_t_r_p:
            for graph_widget in owner.gwObjects:
                if graph_widget.par == parameter:
                    graph_widget.unitMeas = unitMeas
                    break

        if parameter not in list_of_t_r_p:
            new_widget = PlotParameterWorkflowController.create_new_widget(owner, parameter, unitMeas)
            owner.gwObjects.append(new_widget)
            return new_widget

        for gw in owner.gwObjects:
            if gw.par == parameter:
                return gw
        return None

    @staticmethod
    def edit_param_def(owner):
        current_parameter = get_current_parameter()
        user_input = owner.ps.parameter.currentText().upper()
        unitMeas = str(owner.ps.unitMeasurement.text())

        if PlotParameterWorkflowController.parameter_in_plot(owner, user_input) or not PlotParameterWorkflowController.parameter_in_data(owner, user_input):
            return
        print(f"We will replace the parameter {current_parameter} with {user_input}")
        new_widget = PlotParameterWorkflowController.obtain_widget_to_plot(owner, user_input, unitMeas)

        old_widget = None
        for graph_widget in owner.gwObjects:
            if graph_widget.par == current_parameter:
                old_widget = graph_widget
                break

        if old_widget is None:
            print("Could not find existing widget for currPar; aborting edit swap")
            return

        row_number, column_number = PlotParameterWorkflowController.get_widget_location(owner, old_widget)
        owner.scroll_grid_layout.removeWidget(old_widget)
        old_widget.hide()
        new_widget.show()

        owner.scroll_grid_layout.addWidget(new_widget, row_number, column_number)
        owner.scroll_grid_layout.update()

        owner.par[owner.par.index(current_parameter)] = user_input
        set_current_parameter(user_input)
        owner.ps.close()

    @staticmethod
    def create_parameter_dialog(owner, opt, title, add=False):
        global selected_option
        selected_option = opt
        PlotParameterWorkflowController.get_plot_dialog_coordinator(owner).open_dialog(title, add=add)

    @staticmethod
    def add_plot_parameter_dialog(owner):
        selected_option = 'add'
        title = 'Add Plot'
        PlotParameterWorkflowController.create_parameter_dialog(owner, selected_option, title, add=True)

    @staticmethod
    def get_plot_dialog_coordinator(owner):
        coordinator = getattr(owner, "_plot_dialog_coordinator", None)
        if coordinator is None:
            coordinator = PlotParameterDialogCoordinator(
                owner,
                fit_par,
                ParamSpec,
                CustomMessageBox,
            )
            owner._plot_dialog_coordinator = coordinator
        return coordinator

    @staticmethod
    def get_graph_widget_factory(owner):
        factory = getattr(owner, "_graph_widget_factory", None)
        if factory is None:
            factory = PlotParameterWorkflowController._InlineGraphWidgetFactory(owner)
            owner._graph_widget_factory = factory
        return factory

    @staticmethod
    def _build_graph_widget(owner, parameter, unit):
        if parameter not in owner.parameterFittingSettings:
            owner.setEmptyFittingValues(parameter)

        new_widget = IndividualGraphWidget(
            owner.xScale,
            owner.yScale[parameter],
            unit,
            parameter,
            owner.parVals[parameter],
            owner.parValsErr[parameter],
            owner.parValsRADI,
            "Yes",
            owner.numPrecisionX,
            owner.numPrecisionY[parameter],
            owner.pyFAT_Configuration,
            owner.Tirific_Template,
            owner.parameterFittingSettings[parameter],
            PlotParameterWorkflowController._set_plot_scale,
            PolyFitWindow,
        )

        new_widget.setMinimumSize(750, 500)

        new_widget.btnEditParam.clicked.connect(new_widget.changeGlobal)
        new_widget.btnEditParam.clicked.connect(owner.editParaObj)
        new_widget.btnResetParam.clicked.connect(new_widget.changeGlobal)
        new_widget.btnResetParam.clicked.connect(new_widget.reset_parameter_values)
        new_widget.btnCloseParam.clicked.connect(new_widget.changeGlobal)
        new_widget.btnCloseParam.clicked.connect(owner.closeParaObj)
        new_widget.fitting_params_needed.connect(owner.request_fitting_params)
        new_widget.group_right_clicked.connect(owner.show_group_fitting_menu)

        return new_widget
