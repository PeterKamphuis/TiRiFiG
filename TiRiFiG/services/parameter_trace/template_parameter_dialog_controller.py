"""Controller for add-template-parameter dialog state and orchestration helpers."""

from TiRiFiG.services.parameter_trace.template_parameter_dialog_service import TemplateParameterDialogService
from TiRiFiG.services.parameter_trace.template_parameter_service import TemplateParameterService


class TemplateParameterDialogController:
    """Owns derived state for add-template-parameter dialog interactions."""

    def __init__(self, tirific_template, fit_par):
        self.tirific_template = tirific_template
        self.fit_par = fit_par
        self.purpose_options = list(TemplateParameterDialogService.PURPOSE_OPTIONS)
        self.available_by_purpose = TemplateParameterDialogService.available_by_purpose(
            self.tirific_template,
            self.fit_par,
            purpose_options=self.purpose_options,
        )
        self.template_keys_by_purpose = TemplateParameterDialogService.template_keys_by_purpose(
            self.tirific_template,
            self.fit_par,
            purpose_options=self.purpose_options,
        )

    def disk_options(self):
        return TemplateParameterDialogService.disk_options(self.tirific_template)

    def has_available_parameters(self):
        return sum(len(values) for values in self.available_by_purpose.values()) > 0

    def default_purpose(self):
        return next(
            (
                purpose
                for purpose in self.purpose_options
                if len(self.available_by_purpose.get(purpose, [])) > 0
            ),
            self.purpose_options[0],
        )

    def selection_state(self, category_text, disk_text, queued_entries=None):
        try:
            selected_disk = int(float(str(disk_text)))
        except Exception:
            selected_disk = 1
        return TemplateParameterDialogService.selection_state(
            category_text,
            selected_disk,
            self.available_by_purpose,
            self.template_keys_by_purpose,
            self.tirific_template,
            self.fit_par,
            queued_entries=queued_entries,
        )

    def ui_model_from_selection(self, selection_state):
        """Return a UI-agnostic model for rendering dialog widgets."""
        parameter_tooltips = dict(selection_state.get("current_tooltips", {}))
        parameter_items = [
            {
                "text": "Select Parameter",
                "tooltip": "",
            }
        ]
        for parameter_name in selection_state.get("current_available", []):
            parameter_items.append(
                {
                    "text": parameter_name,
                    "tooltip": parameter_tooltips.get(parameter_name, ""),
                }
            )

        after_items = ["End"] + list(selection_state.get("template_keys", []))

        return {
            "show_disk": bool(selection_state.get("show_disk", False)),
            "parameter_items": parameter_items,
            "after_items": after_items,
            "parameter_tooltips": parameter_tooltips,
        }

    def unit_and_initial_state(self, selected_parameter, current_text, last_auto_initial, default_initial):
        unit = TemplateParameterDialogService.unit_for_parameter(selected_parameter, self.fit_par)
        should_update = TemplateParameterDialogService.should_update_initial_value(
            current_text,
            last_auto_initial,
        )
        return {
            "unit": unit,
            "default_initial": default_initial,
            "should_update_initial": should_update,
        }

    def default_template_value_for_parameter(self, parameter, nur_fallback=1):
        """Return default template value for a missing parameter."""
        return TemplateParameterService.default_value_for_parameter(
            parameter,
            self.tirific_template,
            self.fit_par,
            nur_fallback=nur_fallback,
        )

    def insert_parameter(self, parameter_text, after_text="End", initial_value_text="", nur_fallback=1):
        """Validate and insert one parameter into template."""
        queue_result = self.prepare_queue_entry(parameter_text, after_text, initial_value_text)
        if not queue_result.get("ok", False):
            return {
                "ok": False,
                "inserted": False,
                "message": str(queue_result.get("message", "")),
                "parameter": str(parameter_text).upper().strip(),
            }

        entry = queue_result.get("entry", {})
        parameter = str(entry.get("parameter", "")).upper().strip()
        inserted = TemplateParameterService.insert_parameter_in_template(
            parameter,
            str(entry.get("after", "End")),
            self.tirific_template,
            self.fit_par,
            initial_value=str(entry.get("initial_value", "")),
            nur_fallback=nur_fallback,
        )
        return {
            "ok": True,
            "inserted": bool(inserted),
            "message": "",
            "parameter": parameter,
        }

    def prepare_queue_entry(self, parameter_text, after_text="End", initial_value_text=""):
        """Validate and normalize one queue entry from dialog fields."""
        parameter = str(parameter_text).upper().strip()
        if parameter in ["", "SELECT PARAMETER"]:
            return {"ok": False, "message": "", "entry": None}
        if parameter in self.tirific_template:
            return {
                "ok": False,
                "message": f"Parameter {parameter} already exists in the template.",
                "entry": None,
            }

        entry = {
            "parameter": parameter,
            "after": str(after_text).strip() if str(after_text).strip() else "End",
            "initial_value": str(initial_value_text).strip(),
        }
        return {"ok": True, "message": "", "entry": entry}

    def insert_queued_entries(self, queued_entries, nur_fallback=1):
        """Insert queued entries into the template and return insertion stats."""
        added = 0
        inserted_parameters = []

        for entry in queued_entries:
            result = self.insert_parameter(
                entry.get("parameter", ""),
                entry.get("after", "End"),
                entry.get("initial_value", ""),
                nur_fallback=nur_fallback,
            )
            if result.get("inserted", False):
                added += 1
                inserted_parameters.append(result.get("parameter", ""))

        return {
            "added": added,
            "inserted_parameters": inserted_parameters,
        }
