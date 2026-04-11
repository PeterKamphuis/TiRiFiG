"""Service for opening a .def file and building initial graph widgets."""


class OpenDefService:
    """Encapsulate MainWindow.openDef behavior with unchanged flow."""

    @staticmethod
    def open_def(
        owner,
        message_box_cls,
        fat_support_module,
        qt_core,
        qt_widgets,
        np_module,
        set_plot_scale,
        fit_parameters,
    ):
        """Open a definition file, parse parameters, and build graph widgets."""
        owner.data = owner.getData()
        if owner.data is None:
            message_box_cls.information(
                owner,
                "Information",
                "Tilted-ring fitting parameters not retrieved",
            )
            return

        owner.Tirific_Template = fat_support_module.tirific_template(owner.fileName)

        owner.getParameter()
        owner.setPFConfig()
        print(f"Obtained the Parameters from {owner.fileName}")
        owner.getFittingSettings()
        print(f"Obtained the Fitting Settings from {owner.fileName}")

        if owner.runNo > 0:
            message_box_cls.information(
                owner,
                "Information",
                "Close app and reopen to load file. Bug being fixed",
            )
            return

        owner.xScale = set_plot_scale(owner.parValsRADI)
        owner.scrollWidth = owner.scroll_area_content.width()
        owner.scrollHeight = owner.scroll_area_content.height()

        total_params = len(owner.parVals)
        owner.progress = qt_widgets.QProgressDialog(
            "Building graph widgets…",
            None,
            0,
            total_params,
            owner,
        )
        owner.progress.setWindowModality(qt_core.Qt.WindowModality.ApplicationModal)
        owner.progress.setAutoClose(True)
        owner.progress.setAutoReset(False)
        owner.progress.setCancelButton(None)
        owner.progress.setMinimumDuration(0)
        owner.progress.show()
        qt_widgets.QApplication.processEvents()

        g_w_to_plot = {}
        for param_idx, (key, val) in enumerate(owner.parVals.items()):
            owner.progress.setValue(param_idx)
            owner.progress.setLabelText(f"Processing parameter {key}…")
            qt_widgets.QApplication.processEvents()

            diff = owner.NUR - len(val)
            if key == 'RADI':
                if diff == owner.NUR:
                    for j in np_module.arange(0.0, (int(diff) * 40.0), 40):
                        owner.parVals[key].append(j)
                elif diff > 0 and diff < owner.NUR:
                    for _ in range(int(diff)):
                        owner.parVals[key].append(owner.parVals[key][-1] + 40.0)
                continue
            else:
                if diff == owner.NUR:
                    for _ in range(int(diff)):
                        owner.parVals[key].append(0.0)
                elif diff > 0 and diff < owner.NUR:
                    for _ in range(int(diff)):
                        owner.parVals[key].append(val[-1])

            owner.yScale[key] = set_plot_scale(owner.parVals[key])

            unit = fit_parameters[key]["unit"] if key in fit_parameters.keys() else ""
            if key in owner.par:
                new_widget = owner.create_new_widget(key, unit)
                owner.gwObjects.append(new_widget)
                g_w_to_plot[key] = new_widget
                del new_widget

        owner.progress.setValue(total_params)

        ordered_dict_items = [(key, g_w_to_plot[key]) for key in owner.par]
        for idx, items in enumerate(ordered_dict_items):
            graph_widget = items[1]
            owner.scroll_grid_layout.addWidget(graph_widget, idx, 0)
        del g_w_to_plot, ordered_dict_items

        owner.progress.close()
        owner.runNo += 1
