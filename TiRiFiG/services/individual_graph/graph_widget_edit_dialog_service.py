"""Helpers for opening the edit-parameter dialog."""


class GraphWidgetEditDialogService:
    """Encapsulate edit dialog setup and signal wiring for MainWindow."""

    @staticmethod
    def open_edit_dialog(owner, param_spec_cls):
        """Create and show the edit dialog for unplotted parameters."""
        values = []
        for parameter_name in owner.parVals:
            if parameter_name in owner.par:
                continue
            values.append(parameter_name)

        owner.ps = param_spec_cls(values, "Edit Parameter")
        owner.ps.show()
        owner.ps.btnOK.clicked.connect(owner.editParamDef)
        owner.ps.btnCancel.clicked.connect(owner.ps.close)
