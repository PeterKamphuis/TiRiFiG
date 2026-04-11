"""Pure helpers for add-parameter dialog option generation."""

import re


class TemplateParameterDialogService:
    """Build category/disk dependent parameter options without Qt dependencies."""

    PURPOSE_OPTIONS = ["overhead", "model", "fitting"]

    @staticmethod
    def disk_options(tirific_template):
        """Return selectable disk numbers as strings, including one extra disk."""
        ndisks_value = tirific_template.get("NDISK", tirific_template.get("NDISKS", "1"))
        try:
            number_of_disks = int(float(str(ndisks_value).split()[0]))
        except Exception:
            number_of_disks = 1
        number_of_disks = max(1, number_of_disks)
        return [str(i) for i in range(1, number_of_disks + 2)]

    @staticmethod
    def disk_for_parameter(parameter_key):
        """Return disk number parsed from a parameter suffix."""
        parameter_key = str(parameter_key).upper().strip()
        match = re.search(r"_(\d+)$", parameter_key)
        if match is None:
            return 1
        try:
            disk_num = int(match.group(1))
        except Exception:
            return 1
        return max(1, disk_num)

    @staticmethod
    def meta_key_for_parameter_name(parameter_name, fit_par):
        """Return metadata key for parameter name, normalizing _<n> to _i when needed."""
        parameter_name = str(parameter_name).upper().strip()
        if parameter_name in fit_par:
            return parameter_name
        normalized = re.sub(r"_\d+$", "_i", parameter_name)
        if normalized in fit_par:
            return normalized
        return None

    @staticmethod
    def available_by_purpose(tirific_template, fit_par, purpose_options=None):
        """Return addable parameters grouped by purpose."""
        if purpose_options is None:
            purpose_options = TemplateParameterDialogService.PURPOSE_OPTIONS
        grouped = {}
        for selected_purpose in purpose_options:
            available = []
            for key in fit_par.keys():
                if any(ch.islower() for ch in key):
                    continue
                if "=" in key:
                    continue
                if str(fit_par.get(key, {}).get("purpose", "")).lower() != selected_purpose:
                    continue
                if selected_purpose == "model":
                    available.append(key)
                elif key not in tirific_template:
                    available.append(key)
            grouped[selected_purpose] = sorted(available)
        return grouped

    @staticmethod
    def template_keys_by_purpose(tirific_template, fit_par, purpose_options=None):
        """Return existing template keys grouped by purpose (non-model only)."""
        if purpose_options is None:
            purpose_options = TemplateParameterDialogService.PURPOSE_OPTIONS
        grouped = {}
        for selected_purpose in purpose_options:
            if selected_purpose != "model":
                grouped[selected_purpose] = [
                    key for key in tirific_template.keys()
                    if not str(key).upper().startswith("EMPTY")
                    and key in fit_par
                    and str(fit_par.get(key, {}).get("purpose", "")).lower() == selected_purpose
                ]
            else:
                grouped[selected_purpose] = []
        return grouped

    @staticmethod
    def current_available(selected_purpose, selected_disk, available_by_purpose, tirific_template, fit_par):
        """Return currently available parameters for selected purpose and disk."""
        current_available = list(available_by_purpose.get(selected_purpose, []))
        if selected_purpose == "model":
            if selected_disk <= 1:
                current_available = [
                    parameter for parameter in current_available
                    if parameter not in tirific_template
                ]
            else:
                disk_specific = []
                for base_parameter in current_available:
                    if f"{base_parameter}_i" not in fit_par:
                        continue
                    resolved_name = f"{base_parameter}_{selected_disk}"
                    if resolved_name in tirific_template:
                        continue
                    disk_specific.append(resolved_name)
                current_available = sorted(set(disk_specific))
        return current_available

    @staticmethod
    def queued_parameters_for_selection(queued_entries, selected_purpose, selected_disk, fit_par):
        """Return queued parameters that match current purpose/disk selection."""
        queued_parameters = set()
        for entry in queued_entries:
            queued_parameter = str(entry.get("parameter", "")).upper().strip()
            meta_key = TemplateParameterDialogService.meta_key_for_parameter_name(queued_parameter, fit_par)
            if meta_key is None:
                continue
            if str(fit_par.get(meta_key, {}).get("purpose", "")).lower() != selected_purpose:
                continue
            if selected_purpose == "model" and TemplateParameterDialogService.disk_for_parameter(queued_parameter) != selected_disk:
                continue
            queued_parameters.add(queued_parameter)
        return queued_parameters

    @staticmethod
    def tooltips_for_parameters(parameter_names, fit_par):
        """Return explanation tooltips for current parameter names."""
        tooltips = {}
        for parameter_name in parameter_names:
            meta_key = TemplateParameterDialogService.meta_key_for_parameter_name(parameter_name, fit_par)
            if meta_key is not None:
                tooltips[parameter_name] = fit_par.get(meta_key, {}).get("explanation", "")
        return tooltips

    @staticmethod
    def template_keys_for_after(selected_purpose, selected_disk, template_keys_by_purpose, tirific_template, fit_par):
        """Return ordered Add-After candidates for selected purpose/disk."""
        if selected_purpose == "model":
            template_keys = []
            for key in tirific_template.keys():
                key_upper = str(key).upper().strip()
                if key_upper.startswith("EMPTY"):
                    continue
                meta_key = TemplateParameterDialogService.meta_key_for_parameter_name(key_upper, fit_par)
                if meta_key is None:
                    continue
                if str(fit_par.get(meta_key, {}).get("purpose", "")).lower() != selected_purpose:
                    continue
                if TemplateParameterDialogService.disk_for_parameter(key_upper) != selected_disk:
                    continue
                template_keys.append(key_upper)
            template_keys = sorted(set(template_keys))
        else:
            template_keys = list(template_keys_by_purpose.get(selected_purpose, []))

        if selected_purpose == "model":
            template_keys = [
                parameter for parameter in template_keys
                if TemplateParameterDialogService.disk_for_parameter(parameter) == selected_disk
            ]
        return template_keys

    @staticmethod
    def selection_state(
        selected_purpose,
        selected_disk,
        available_by_purpose,
        template_keys_by_purpose,
        tirific_template,
        fit_par,
        queued_entries=None,
    ):
        """Build all computed state needed to repaint category/disk-driven UI widgets."""
        purpose = str(selected_purpose).strip().lower()
        try:
            disk = int(float(selected_disk))
        except Exception:
            disk = 1
        disk = max(1, disk)

        current_available = TemplateParameterDialogService.current_available(
            purpose,
            disk,
            available_by_purpose,
            tirific_template,
            fit_par,
        )

        queued_parameters = set()
        if queued_entries is not None:
            queued_parameters = TemplateParameterDialogService.queued_parameters_for_selection(
                queued_entries,
                purpose,
                disk,
                fit_par,
            )

        current_available = [p for p in current_available if p not in queued_parameters]
        current_tooltips = TemplateParameterDialogService.tooltips_for_parameters(
            current_available,
            fit_par,
        )
        template_keys = TemplateParameterDialogService.template_keys_for_after(
            purpose,
            disk,
            template_keys_by_purpose,
            tirific_template,
            fit_par,
        )

        return {
            "selected_purpose": purpose,
            "selected_disk": disk,
            "show_disk": purpose == "model",
            "current_available": current_available,
            "current_tooltips": current_tooltips,
            "template_keys": template_keys,
        }

    @staticmethod
    def unit_for_parameter(parameter_name, fit_par):
        """Return unit metadata for a parameter, normalizing disk suffixes when needed."""
        meta_key = TemplateParameterDialogService.meta_key_for_parameter_name(parameter_name, fit_par)
        if meta_key is None:
            return ""
        return str(fit_par.get(meta_key, {}).get("unit", ""))

    @staticmethod
    def should_update_initial_value(current_text, last_auto_initial):
        """Return True when auto-initial should replace current textbox value."""
        current = str(current_text).strip()
        return current == "" or current == str(last_auto_initial)
