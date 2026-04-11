"""Template parameter insertion and default-value helpers."""

import re


class TemplateParameterService:
    """Pure helpers for adding parameters to a TiRiFiC template."""

    @staticmethod
    def default_value_for_parameter(parameter, tirific_template, fit_par, nur_fallback=1):
        """Build a sensible default value string for a newly added template parameter."""
        meta_key = str(parameter).upper().strip()
        if meta_key not in fit_par:
            meta_key = re.sub(r"_\d+$", "_i", meta_key)
        meta = fit_par.get(meta_key, {})
        purpose = str(meta.get("purpose", "")).lower()
        parameter_upper = str(parameter).upper().strip()

        if purpose == "model":
            target_match = re.search(r"_(\d+)$", parameter_upper)
            target_disk = int(target_match.group(1)) if target_match else 1
            base_parameter = re.sub(r"_\d+$", "", parameter_upper)

            closest_candidates = []
            for existing_key in tirific_template.keys():
                existing_upper = str(existing_key).upper().strip()
                if existing_upper.startswith("EMPTY"):
                    continue
                if re.sub(r"_\d+$", "", existing_upper) != base_parameter:
                    continue

                existing_meta_key = existing_upper if existing_upper in fit_par else re.sub(r"_\d+$", "_i", existing_upper)
                existing_purpose = str(fit_par.get(existing_meta_key, {}).get("purpose", "")).lower()
                if existing_purpose != "model":
                    continue

                disk_match = re.search(r"_(\d+)$", existing_upper)
                existing_disk = int(disk_match.group(1)) if disk_match else 1
                if existing_disk == target_disk:
                    continue

                existing_value = str(tirific_template.get(existing_key, "")).strip()
                if existing_value == "":
                    continue
                closest_candidates.append((abs(existing_disk - target_disk), existing_disk, existing_value))

            if len(closest_candidates) > 0:
                closest_candidates.sort(key=lambda item: (item[0], item[1]))
                return closest_candidates[0][2]

        category = str(meta.get("category", "")).upper()
        if category == "GEOMETRICAL":
            try:
                nur = int(float(str(tirific_template.get("NUR", "0")).split()[0]))
            except Exception:
                nur = int(nur_fallback) if nur_fallback else 1
            nur = max(1, nur)
            return " ".join(["0"] * nur)
        return ""

    @staticmethod
    def insert_parameter_in_template(parameter, after_parameter, tirific_template, fit_par, initial_value=None, nur_fallback=1):
        """Insert a new parameter key into Tirific_Template after a chosen key."""
        parameter = str(parameter).upper().strip()
        after_parameter = str(after_parameter).upper().strip()

        ndisks_value = tirific_template.get("NDISK", tirific_template.get("NDISKS", "1"))
        try:
            number_of_disks = int(float(str(ndisks_value).split()[0]))
        except Exception:
            number_of_disks = 1
        number_of_disks = max(1, number_of_disks)

        def _maybe_expand_ndisks_from_parameter(parameter_name):
            suffix_match = re.search(r"_(\d+)$", str(parameter_name).upper().strip())
            if suffix_match is None:
                return
            try:
                parameter_disk = int(suffix_match.group(1))
            except Exception:
                return
            if parameter_disk <= number_of_disks:
                return
            updated_disks = str(parameter_disk)
            tirific_template["NDISKS"] = updated_disks
            if "NDISK" in tirific_template:
                tirific_template["NDISK"] = updated_disks

        if not parameter or parameter == "SELECT PARAMETER":
            return False
        if parameter in tirific_template:
            return False

        raw_initial = "" if initial_value is None else str(initial_value).strip()
        if raw_initial != "":
            if " " in raw_initial:
                new_value = raw_initial
            else:
                meta_key = str(parameter).upper().strip()
                if meta_key not in fit_par:
                    meta_key = re.sub(r"_\d+$", "_i", meta_key)
                meta = fit_par.get(meta_key, {})
                category = str(meta.get("category", "")).upper()
                if category == "GEOMETRICAL":
                    try:
                        nur = int(float(str(tirific_template.get("NUR", "0")).split()[0]))
                    except Exception:
                        nur = int(nur_fallback) if nur_fallback else 1
                    nur = max(1, nur)
                    new_value = " ".join([raw_initial] * nur)
                else:
                    new_value = raw_initial
        else:
            new_value = TemplateParameterService.default_value_for_parameter(
                parameter,
                tirific_template,
                fit_par,
                nur_fallback=nur_fallback,
            )

        keys = list(tirific_template.keys())

        if len(keys) == 0:
            tirific_template[parameter] = new_value
            _maybe_expand_ndisks_from_parameter(parameter)
            return True

        if after_parameter not in ["", "END"] and after_parameter in tirific_template:
            insert_after = after_parameter
        else:
            parameter_meta_key = parameter if parameter in fit_par else re.sub(r"_\d+$", "_i", parameter)
            parameter_purpose = str(fit_par.get(parameter_meta_key, {}).get("purpose", "")).lower()
            if after_parameter in ["", "END"] and parameter_purpose == "model":
                last_model_key = None
                for key in keys:
                    key_upper = str(key).upper().strip()
                    if key_upper.startswith("EMPTY"):
                        continue
                    key_meta = key_upper if key_upper in fit_par else re.sub(r"_\d+$", "_i", key_upper)
                    if str(fit_par.get(key_meta, {}).get("purpose", "")).lower() == "model":
                        last_model_key = key
                insert_after = last_model_key if last_model_key is not None else keys[-1]
            else:
                insert_after = keys[-1]

        if not hasattr(tirific_template, "insert"):
            # Safety fallback for unexpected template implementations.
            tirific_template[parameter] = new_value
            _maybe_expand_ndisks_from_parameter(parameter)
            return True

        # Support multiple insert signatures used by different OrderedDict-like classes.
        inserted = False
        for args in [
            (insert_after, parameter, new_value),
            (parameter, new_value, insert_after),
            (parameter, insert_after, new_value),
        ]:
            try:
                tirific_template.insert(*args)
                inserted = True
                break
            except TypeError:
                continue

        if not inserted:
            # Last-resort fallback if signature is unexpected.
            tirific_template[parameter] = new_value

        _maybe_expand_ndisks_from_parameter(parameter)
        return True
