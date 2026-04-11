"""Service for syncing graph widgets after .def file edits."""


class SlotChangeDataService:
    """Encapsulate MainWindow.slotChangeData behavior with unchanged flow."""

    @staticmethod
    def slot_change_data(owner, file_name, fit_parameters, np_module, ceil_fn, set_plot_scale):
        """Reload values from file and refresh all graph widgets."""
        with open(file_name) as file_handle:
            owner.data = file_handle.readlines()

        owner.getParameter(owner.data)

        for parameter in fit_parameters.keys():
            for graph_widget in owner.gwObjects:
                if graph_widget.par == parameter:
                    graph_widget.parVals = owner.parVals[parameter][:]
                    graph_widget.parValRADI = owner.parValsRADI[parameter][:]

        owner.xScale = set_plot_scale(owner.gwObjects[0].parValRADI)

        for graph_widget in owner.gwObjects:
            if graph_widget.historyList[len(graph_widget.historyList) - 1] != graph_widget.parVals[:]:
                graph_widget.historyList.append(graph_widget.parVals[:])

            graph_widget.xScale = owner.xScale
            if np_module.subtract(max(graph_widget.parVals), min(graph_widget.parVals)) == 0:
                graph_widget.yScale = [-100, 100]
            elif (max(graph_widget.parVals) - min(graph_widget.parVals)) <= 100:
                graph_widget.yScale = [
                    int(ceil_fn(-2 * max(graph_widget.parVals))),
                    int(ceil_fn(2 * max(graph_widget.parVals))),
                ]
            else:
                graph_widget.yScale = [
                    int(
                        ceil_fn(
                            min(graph_widget.parVals)
                            - 0.1 * (max(graph_widget.parVals) - min(graph_widget.parVals))
                        )
                    ),
                    int(
                        ceil_fn(
                            max(graph_widget.parVals)
                            + 0.1 * (max(graph_widget.parVals) - min(graph_widget.parVals))
                        )
                    ),
                ]
            graph_widget.firstPlot()
