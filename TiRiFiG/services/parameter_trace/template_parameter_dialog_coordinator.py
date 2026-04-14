"""Coordinator for opening and wiring the add-template-parameter dialog."""

from TiRiFiG.classes.classes import DialogCoordinatorBase
from TiRiFiG.services.individual_graph.plot_scale_helper import set_plot_scale
from TiRiFiG.services.parameter_trace.template_parameter_dialog_controller import TemplateParameterDialogController
from TiRiFiG.services.parameter_trace.template_parameter_dialog_presenter import TemplateParameterDialogSignalFacade


class TemplateParameterDialogCoordinator(DialogCoordinatorBase):
    """Build and wire ParamSpec for template-parameter management."""

    def __init__(self, owner, fit_par, param_spec_cls, message_box_cls):
        super().__init__(owner, fit_par, param_spec_cls, message_box_cls)

    def queue_current_parameter(self):
        """Queue one template parameter from dialog selection."""
        owner = self.owner
        controller = owner._template_dialog_controller
        after_parameter = owner.ps.afterParameter.currentText() if hasattr(owner.ps, "afterParameter") else "End"
        initial_value = ""
        if hasattr(owner.ps, "initialValue") and owner.ps.initialValue is not None:
            initial_value = owner.ps.initialValue.text().strip()

        queue_result = controller.prepare_queue_entry(
            owner.ps.parameter.currentText(),
            after_parameter,
            initial_value,
        )
        if not queue_result.get("ok", False):
            message = str(queue_result.get("message", "")).strip()
            if message:
                self.info(message)
            return

        entry = queue_result.get("entry", {})
        owner.ps.add_queued_parameter(
            entry.get("parameter", ""),
            entry.get("after", "End"),
            initial_value=entry.get("initial_value", ""),
        )

    def add_queued_parameters(self):
        """Insert all queued template parameters in list order."""
        owner = self.owner
        queued = owner.ps.get_queued_parameters_with_meta() if hasattr(owner.ps, "get_queued_parameters_with_meta") else []
        if len(queued) == 0:
            self.info("No queued parameters to add")
            return

        controller = owner._template_dialog_controller
        insert_result = controller.insert_queued_entries(
            queued,
            nur_fallback=owner.NUR,
        )
        added = int(insert_result.get("added", 0))

        if added > 0:
            owner.getParameter()
            for key in owner.parVals:
                if key not in owner.yScale:
                    owner.yScale[key] = set_plot_scale(owner.parVals[key])

        self.info(f"Added {added} parameter(s) to template.")
        owner.ps.close()

    def open_dialog(self, title, add=True):
        owner = self.owner
        owner._template_dialog_controller = TemplateParameterDialogController(
            owner.Tirific_Template,
            self.fit_par,
        )
        controller = owner._template_dialog_controller

        if not controller.has_available_parameters():
            self.info("No additional parameters available to add.")
            return

        disk_options = controller.disk_options()
        purpose_options = controller.purpose_options
        available_by_purpose = controller.available_by_purpose
        template_keys_by_purpose = controller.template_keys_by_purpose
        default_purpose = controller.default_purpose()

        owner.ps = self.param_spec_cls(
            available_by_purpose[default_purpose],
            title,
            plotted_parameters=template_keys_by_purpose[default_purpose],
            addLocation=True,
            parameterTooltips={},
            categories=purpose_options,
            disks=disk_options,
            showInitialValue=True,
        )

        if owner.ps.category is not None:
            owner.ps.category.setCurrentText(default_purpose)

        if hasattr(owner.ps, "disk") and owner.ps.disk is not None:
            owner.ps.disk.setCurrentIndex(0)

        owner._template_dialog_signal_facade = TemplateParameterDialogSignalFacade(
            owner.ps,
            controller,
            nur_fallback=owner.NUR,
        )

        if owner.ps.category is not None:
            owner.ps.category.currentTextChanged.connect(
                lambda category_text: owner._template_dialog_signal_facade.apply_category_state(category_text)
            )
            owner._template_dialog_signal_facade.apply_category_state(owner.ps.category.currentText())

        if hasattr(owner.ps, "disk") and owner.ps.disk is not None:
            owner.ps.disk.currentTextChanged.connect(
                lambda _text: owner._template_dialog_signal_facade.apply_category_state(
                    owner.ps.category.currentText() if owner.ps.category is not None else default_purpose
                )
            )

        owner.ps.parameter.currentTextChanged.connect(
            lambda _text: owner._template_dialog_signal_facade.sync_parameter_selection()
        )
        owner._template_dialog_signal_facade.sync_parameter_selection()

        if add:
            owner.ps.btnOK.clicked.connect(self.queue_current_parameter)
            if owner.ps.btnAddParameters is not None:
                owner.ps.btnAddParameters.clicked.connect(self.add_queued_parameters)
        else:
            owner.ps.btnOK.clicked.connect(self.queue_current_parameter)
        owner.ps.btnCancel.clicked.connect(owner.ps.close)
        owner.ps.show()
