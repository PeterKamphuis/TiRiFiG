"""Service for saving all current parameter and fitting changes."""


class SaveAllService:
    """Encapsulate MainWindow.saveAll behavior with unchanged flow."""

    @staticmethod
    def save_all(owner, np_module):
        """Persist all graph values and fitting settings to the current .def file."""
        owner.saveParameter(
            owner.parValsRADI,
            np_module.array([float('NaN')] * len(owner.parValsRADI)),
            'RADI',
            owner.numPrecisionX,
        )

        # Reset the fitting parameters before rebuilding them from current widgets.
        for fit_key in owner.fitting_parameters:
            owner.Tirific_Template[fit_key] = ''

        for graph_widget in owner.gwObjects:
            owner.saveParameter(
                graph_widget.parVals,
                graph_widget.parValsErr,
                graph_widget.par,
                graph_widget.numPrecisionY,
            )
            if graph_widget.parameterFitSetting['TO_FIT']:
                if graph_widget.parameterFitSetting['PARMAX'] is None:
                    graph_widget.parameterFitSetting['PARMAX'] = graph_widget.yScale[1]
                if graph_widget.parameterFitSetting['PARMIN'] is None:
                    graph_widget.parameterFitSetting['PARMIN'] = graph_widget.yScale[0]
                owner.parameterFittingSettings[graph_widget.par] = graph_widget.parameterFitSetting

        owner.updateFitSettings()
        owner.write_tirific()
        owner.saveMessage()
