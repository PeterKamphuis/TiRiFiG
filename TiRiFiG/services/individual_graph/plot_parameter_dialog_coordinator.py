"""Coordinator for opening and handling the add-plot-parameter dialog."""

from TiRiFiG.classes.classes import DialogCoordinatorBase


class PlotParameterDialogCoordinator(DialogCoordinatorBase):
    """Build and wire ParamSpec for plotting-parameter management."""

    def __init__(self, owner, fit_par, param_spec_cls, message_box_cls, workflow_cls):
        super().__init__(owner, fit_par, param_spec_cls, message_box_cls)
        self.workflow_cls = workflow_cls

    def open_dialog(self, title, add=False):
        owner = self.owner
        values = []
        parameter_tooltips = {}
        for key in owner.parVals:
            if key in owner.par:
                continue
            values.append(key)
            parameter_tooltips[key] = self.fit_par[key]["explanation"] if key in self.fit_par else ""

        owner.ps = self.param_spec_cls(
            values,
            title,
            plotted_parameters=owner.par,
            addLocation=add,
            parameterTooltips=parameter_tooltips,
        )
        owner.ps.show()

        if add:
            owner.ps.btnOK.clicked.connect(self.queue_current_parameter)
            if owner.ps.btnAddParameters is not None:
                owner.ps.btnAddParameters.clicked.connect(self.add_queued_parameters)
        else:
            owner.ps.btnOK.clicked.connect(lambda: self.workflow_cls.param_def(owner))
        owner.ps.btnCancel.clicked.connect(owner.ps.close)

    def queue_current_parameter(self):
        """Queue one parameter from add-plot dialog without inserting yet."""
        owner = self.owner
        user_input = owner.ps.parameter.currentText().upper()
        if user_input in ["", "SELECT PARAMETER"]:
            return
        if self.workflow_cls.parameter_in_plot(owner, user_input) or not self.workflow_cls.parameter_in_data(owner, user_input):
            return
        after_parameter = owner.ps.afterParameter.currentText()
        owner.ps.add_queued_parameter(user_input, after_parameter)

    def add_queued_parameters(self):
        """Insert queued plot parameters in list order."""
        owner = self.owner
        unit_meas = str(owner.ps.unitMeasurement.text())
        queued = owner.ps.get_queued_parameters()
        if len(queued) == 0:
            self.info("No queued parameters to add")
            return

        owner.progress.setLabelText("Adding parameters…")
        owner.progress.setMaximum(len(queued))
        owner.progress.setValue(0)
        owner.progress.show()
        self.process_events()

        for idx, (user_input, after_parameter) in enumerate(queued):
            owner.progress.setValue(idx)
            owner.progress.setLabelText(f"Adding parameter {user_input}…")
            self.process_events()
            if self.workflow_cls.parameter_in_plot(owner, user_input) or not self.workflow_cls.parameter_in_data(owner, user_input):
                continue
            self.workflow_cls.insert_parameter_in_layout(owner, user_input, unit_meas, after_parameter)

        owner.progress.setValue(len(queued))
        owner.progress.close()
        owner.ps.close()
