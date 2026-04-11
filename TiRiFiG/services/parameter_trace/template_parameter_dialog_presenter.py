"""Presenter utilities for applying add-template-parameter dialog UI models."""

from PyQt6 import QtCore


class TemplateParameterDialogPresenter:
    """Apply controller-built UI models to ParamSpec dialog widgets."""

    @staticmethod
    def apply_ui_model(param_spec_dialog, ui_model):
        """Apply one UI model object to add-template-parameter dialog controls."""
        visible = bool(ui_model.get("show_disk", False))
        if hasattr(param_spec_dialog, "diskLabel") and param_spec_dialog.diskLabel is not None:
            param_spec_dialog.diskLabel.setVisible(visible)
        if hasattr(param_spec_dialog, "disk") and param_spec_dialog.disk is not None:
            param_spec_dialog.disk.setVisible(visible)

        parameter_items = list(ui_model.get("parameter_items", []))
        param_spec_dialog.parameter.blockSignals(True)
        param_spec_dialog.parameter.clear()
        for item in parameter_items:
            text = str(item.get("text", ""))
            tooltip = str(item.get("tooltip", ""))
            param_spec_dialog.parameter.addItem(text)
            idx = param_spec_dialog.parameter.count() - 1
            if tooltip:
                param_spec_dialog.parameter.setItemData(
                    idx,
                    tooltip,
                    QtCore.Qt.ItemDataRole.ToolTipRole,
                )
        if param_spec_dialog.parameter.count() == 0:
            param_spec_dialog.parameter.addItem("Select Parameter")
        param_spec_dialog.parameter.setCurrentIndex(0)
        param_spec_dialog.parameter.blockSignals(False)
        param_spec_dialog.parameter.setToolTip("")

        if hasattr(param_spec_dialog, "afterParameter") and param_spec_dialog.afterParameter is not None:
            param_spec_dialog.afterParameter.clear()
            for value in list(ui_model.get("after_items", ["End"])):
                param_spec_dialog.afterParameter.addItem(str(value))
            end_idx = param_spec_dialog.afterParameter.findText("End", QtCore.Qt.MatchFlag.MatchFixedString)
            if end_idx >= 0:
                param_spec_dialog.afterParameter.setCurrentIndex(end_idx)


class TemplateParameterDialogSignalFacade:
    """Handle dialog signal reactions using controller and presenter."""

    def __init__(self, param_spec_dialog, controller, nur_fallback=1):
        self.dialog = param_spec_dialog
        self.controller = controller
        self.nur_fallback = nur_fallback
        self.sync_state = {"last_auto_initial": ""}

    def apply_category_state(self, category_text):
        selected_disk_text = "1"
        if hasattr(self.dialog, "disk") and self.dialog.disk is not None:
            selected_disk_text = self.dialog.disk.currentText()

        queued_entries = []
        if self.dialog.parameterQueue is not None and hasattr(self.dialog, "get_queued_parameters_with_meta"):
            queued_entries = self.dialog.get_queued_parameters_with_meta()

        selection_state = self.controller.selection_state(
            category_text,
            selected_disk_text,
            queued_entries=queued_entries,
        )

        ui_model = self.controller.ui_model_from_selection(selection_state)
        self.dialog.parameterTooltips = ui_model.get("parameter_tooltips", {})
        TemplateParameterDialogPresenter.apply_ui_model(self.dialog, ui_model)
        self.dialog.unitMeasurement.clear()

    def sync_parameter_selection(self):
        selected = str(self.dialog.parameter.currentText()).upper().strip()
        current_text = ""
        if hasattr(self.dialog, "initialValue") and self.dialog.initialValue is not None:
            current_text = self.dialog.initialValue.text().strip()

        default_initial = self.controller.default_template_value_for_parameter(
            selected,
            nur_fallback=self.nur_fallback,
        )
        sync_values = self.controller.unit_and_initial_state(
            selected,
            current_text,
            self.sync_state.get("last_auto_initial", ""),
            default_initial,
        )

        self.dialog.unitMeasurement.setText(sync_values["unit"])

        if hasattr(self.dialog, "initialValue") and self.dialog.initialValue is not None:
            if sync_values["should_update_initial"]:
                self.dialog.initialValue.setText(sync_values["default_initial"])
            self.dialog.initialValue.setPlaceholderText(
                sync_values["default_initial"] if sync_values["default_initial"] else "Optional"
            )
            self.sync_state["last_auto_initial"] = sync_values["default_initial"]
