"""Bootstrap and mapping utilities for fitting settings in the launcher."""

import TRM_errors.tirshaker.tirshaker as fit_functions


class FittingSettingsBootstrapService:
    @staticmethod
    def set_fitting_dialog(owner, message_box_cls, dialog_cls, *args, **kwargs):
        """Open per-parameter fitting dialog with backward-compatible call signature."""
        del args, kwargs
        if owner.parameterFittingSettings is None:
            message_box_cls.information(
                owner,
                "Information",
                "No fitting settings found to modify.",
            )
            return
        owner.fitSettingsDialog = dialog_cls(
            owner.currently_selected_parameter,
            owner.fitting_parameters,
            owner.parameterFittingSettings[owner.currently_selected_parameter],
        )
        owner.fitSettingsDialog.btnOK.clicked.connect(owner.apply_fit_settings)
        owner.fitSettingsDialog.btnCancel.clicked.connect(owner.fitSettingsDialog.close)
        owner.fitSettingsDialog.show()

    @staticmethod
    def get_fitting_settings(owner):
        fit_groups = fit_functions.get_fitted_groups(
            owner.Tirific_Template,
            log=True,
            verbose=True,
        )
        varindex = FittingSettingsBootstrapService.obtain_varindx(owner)
        FittingSettingsBootstrapService.set_ring_fitting_values(owner, fit_groups, varindex)

    @staticmethod
    def set_empty_fitting_values(owner, parameter):
        owner.parameterFittingSettings[parameter] = {"TO_FIT": False}
        for key in owner.fitting_parameters:
            if key not in ["VARY", "VARINDX"]:
                owner.parameterFittingSettings[parameter][key] = None
        for i in range(owner.NUR):
            owner.parameterFittingSettings[parameter][f"RING_{i+1}"] = {
                "TO_FIT": False,
                "INTERPOLATION": False,
                "GROUP": [i + 1, i + 1],
                "BLOCK_FIT": False,
            }
            for key in owner.fitting_parameters:
                if key not in ["VARY", "VARINDX"]:
                    owner.parameterFittingSettings[parameter][f"RING_{i+1}"][key] = None

    @staticmethod
    def set_ring_fitting_values(owner, fit_groups, varindex):
        owner.parameterFittingSettings = {}
        template_values = {}
        for key in owner.fitting_parameters:
            if key not in ["VARY", "VARINDX"]:
                template_values[key] = owner.Tirific_Template[key].split()

        for group in fit_groups:
            basename_group = group.split("_")[0]
            disk = fit_groups[group]["DISKS"]
            for i in disk:
                if i == 1:
                    basename = basename_group
                else:
                    basename = f"{basename_group}_{i}"
                if basename not in owner.parameterFittingSettings:
                    FittingSettingsBootstrapService.set_empty_fitting_values(owner, basename)
                owner.parameterFittingSettings[f"{basename}"]["TO_FIT"] = True
                range_of_rings = fit_groups[group]["RINGS"][f"{i}"]
                for ring in range(range_of_rings[0], range_of_rings[1] + 1):
                    owner.parameterFittingSettings[f"{basename}"][f"RING_{ring}"]["TO_FIT"] = True
                    owner.parameterFittingSettings[f"{basename}"][f"RING_{ring}"]["GROUP"] = range_of_rings
                    owner.parameterFittingSettings[f"{basename}"][f"RING_{ring}"]["BLOCK_FIT"] = fit_groups[group]["BLOCK"]
                    if basename in varindex:
                        if ring in varindex[basename]:
                            owner.parameterFittingSettings[f"{basename}"][f"RING_{ring}"]["INTERPOLATION"] = True
                    for key in owner.fitting_parameters:
                        if key not in ["VARY", "VARINDX"]:
                            template_value = template_values[key]
                            if len(template_value) == len(fit_groups):
                                if key in ["ITESTART", "ITEEND", "MODERATE"]:
                                    put_value = int(float(template_value[fit_groups[group]["COLUMN_ID"]]))
                                else:
                                    put_value = float(template_value[fit_groups[group]["COLUMN_ID"]])
                                owner.parameterFittingSettings[f"{basename}"][f"RING_{ring}"][key] = put_value
                                if owner.parameterFittingSettings[f"{basename}"][key] is None:
                                    owner.parameterFittingSettings[f"{basename}"][key] = put_value

    @staticmethod
    def obtain_varindx(owner):
        varindex = {}
        varindx_line = owner.Tirific_Template["VARINDX"].split()
        for i in range(len(varindx_line)):
            try:
                value = int(float(varindx_line[i]))
            except Exception:
                if ":" in varindx_line[i]:
                    parts = varindx_line[i].split(":")

                    rings = [int(float(parts[0])), int(float(parts[1]))]
                    if rings[0] > rings[1]:
                        rings[1] -= 1
                        step = -1
                    else:
                        rings[1] += 1
                        step = 1
                    for j in range(rings[0], rings[1], step):
                        varindex[current_parameter].append(j)
                else:
                    current_parameter = varindx_line[i]
                    if current_parameter not in varindex:
                        varindex[current_parameter] = []
            else:
                varindex[current_parameter].append(value)
        return varindex
