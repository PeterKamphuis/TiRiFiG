"""Controller for fitting-related UI workflow operations."""

from PyQt6 import QtGui, QtWidgets
import numpy as np

from TiRiFiG.classes.classes import CustomMessageBox
from TiRiFiG.services.fitting.fitting_dialog import FittingFillDialog


class FittingWorkflowController:
    """Encapsulate MainWindow fitting dialog and update workflow behaviors."""

    @staticmethod
    def check_fitting(owner):
        fitmode_text = str(owner.Tirific_Template.get('FITMODE', '0')).split()[0]
        try:
            fitmode_value = int(float(fitmode_text))
        except Exception:
            fitmode_value = 0
        optional_when_fitmode2 = {'ITESTART', 'ITEEND', 'SATDELT'}
        for parameter in owner.parameterFittingSettings:
            parValsFitSetting = owner.parameterFittingSettings[parameter]
            if parValsFitSetting['TO_FIT'] == False:
                continue
            ask = False
            for key in owner.fitting_parameters:
                if key not in ['VARY', 'VARINDX']:
                    if fitmode_value == 2 and key in optional_when_fitmode2:
                        continue
                    if parValsFitSetting[key] is None:
                        for ring_num in range(1, owner.NUR):
                            ring_key = f"RING_{ring_num}"
                            ring_values = []
                            if parValsFitSetting[ring_key][key] is not None:
                                ring_values.append(parValsFitSetting[ring_key][key])
                        if len(ring_values) > 0:
                            owner.parameterFittingSettings[parameter][key] = np.mean(
                                np.array(ring_values, dtype=float)
                            )
                        elif key in ['ITESTART', 'ITEEND', 'MODERATE']:
                            for parch in owner.parameterFittingSettings:
                                found = []
                                if owner.parameterFittingSettings[parch][key] is not None:
                                    found.append(owner.parameterFittingSettings[parch][key])
                            if len(found) > 0:
                                owner.parameterFittingSettings[parameter][key] = int(
                                    np.mean(np.array(found, dtype=int))
                                )
                            else:
                                ask = True
                        else:
                            ask = True
            if ask:
                owner.dialog = FittingFillDialog(
                    parameter,
                    owner.fitting_parameters,
                    parValsFitSetting,
                )
                owner.dialog.btnOK.clicked.connect(owner.dialog.accept)
                owner.dialog.btnCancel.clicked.connect(owner.dialog.reject)
                result = owner.dialog.exec()
                if result == QtWidgets.QDialog.DialogCode.Accepted:
                    FittingWorkflowController.fill_fitting_values(owner)
                else:
                    return

    @staticmethod
    def fill_fitting_values(owner):
        parameter = owner.dialog.parameter
        for key in owner.fitting_parameters:
            if key not in ['VARY', 'VARINDX']:
                value_text = getattr(owner.dialog, key).text()
                if value_text != '':
                    try:
                        if key in ['ITESTART', 'ITEEND', 'MODERATE']:
                            value = int(float(value_text))
                        else:
                            value = float(value_text)
                    except Exception:
                        CustomMessageBox.information(
                            owner,
                            "Information",
                            f"Invalid value for {key}. Must be a number.",
                        )
                        return
                    owner.parameterFittingSettings[parameter][key] = value
        owner.dialog.close()

    @staticmethod
    def show_group_fitting_menu(owner, parameter, min_ring, max_ring):
        menu = QtWidgets.QMenu(owner)
        label = f"Edit fitting parameters  (rings {min_ring}\u2013{max_ring})"
        edit_action = menu.addAction(label)
        chosen = menu.exec(QtGui.QCursor.pos())
        if chosen == edit_action:
            FittingWorkflowController.edit_group_fitting(owner, parameter, min_ring, max_ring)

    @staticmethod
    def edit_group_fitting(owner, parameter, min_ring, max_ring):
        parValsFitSetting = owner.parameterFittingSettings[parameter]
        ring_key = f"RING_{min_ring}"
        ring_settings = parValsFitSetting.get(ring_key, {})
        merged = {}
        for key in owner.fitting_parameters:
            if key not in ['VARY', 'VARINDX']:
                ring_val = ring_settings.get(key)
                global_val = parValsFitSetting.get(key)
                merged[key] = ring_val if ring_val is not None else global_val
        owner._group_edit_context = (parameter, min_ring, max_ring)
        owner.dialog = FittingFillDialog(parameter, owner.fitting_parameters, merged)
        owner.dialog.setWindowTitle(
            f"Fitting Parameters — {parameter} rings {min_ring}\u2013{max_ring}"
        )
        owner.dialog.btnOK.clicked.connect(owner.dialog.accept)
        owner.dialog.btnCancel.clicked.connect(owner.dialog.reject)
        result = owner.dialog.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            FittingWorkflowController.fill_group_fitting_values(owner)

    @staticmethod
    def fill_group_fitting_values(owner):
        parameter, min_ring, max_ring = owner._group_edit_context
        for key in owner.fitting_parameters:
            if key not in ['VARY', 'VARINDX']:
                value_text = getattr(owner.dialog, key).text().strip()
                if not value_text:
                    value_text = getattr(owner.dialog, key).placeholderText().strip()
                if value_text:
                    try:
                        if key in ['ITESTART', 'ITEEND', 'MODERATE']:
                            value = int(float(value_text))
                        else:
                            value = float(value_text)
                    except ValueError:
                        continue
                    for ring in range(min_ring, max_ring + 1):
                        rk = f"RING_{ring}"
                        if rk in owner.parameterFittingSettings[parameter]:
                            owner.parameterFittingSettings[parameter][rk][key] = value
        owner.dialog.close()

    @staticmethod
    def request_fitting_params(owner, parameter):
        parValsFitSetting = owner.parameterFittingSettings[parameter]
        fitting_keys = [k for k in owner.fitting_parameters if k not in ['VARY', 'VARINDX']]
        fitmode_text = str(owner.Tirific_Template.get('FITMODE', '0')).split()[0]
        try:
            fitmode_value = int(float(fitmode_text))
        except Exception:
            fitmode_value = 0
        if fitmode_value == 2:
            fitting_keys = [k for k in fitting_keys if k not in ['SATDELT', 'ITESTART', 'ITEEND']]
        if not any(parValsFitSetting.get(k) is None for k in fitting_keys):
            return
        owner.dialog = FittingFillDialog(parameter, owner.fitting_parameters, parValsFitSetting)
        owner.dialog.btnOK.clicked.connect(owner.dialog.accept)
        owner.dialog.btnCancel.clicked.connect(owner.dialog.reject)
        result = owner.dialog.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            FittingWorkflowController.fill_fitting_values(owner)

    @staticmethod
    def update_fit_settings(owner):
        FittingWorkflowController.check_fitting(owner)
        for parameter in owner.parameterFittingSettings:
            numPrecision = owner.numPrecisionY[parameter]
            parValsFitSetting = owner.parameterFittingSettings[parameter]
            precision = f'.{numPrecision[0]}{numPrecision[1].lower()}'
            if not parValsFitSetting['TO_FIT']:
                continue
            else:
                fitting_blocks = []
                interpolation_rings = []
                processed = []
                for ring_num in range(1, owner.NUR):
                    ring_key = f"RING_{ring_num}"
                    ring_setting = parValsFitSetting[ring_key]
                    if ring_setting['INTERPOLATION'] and ring_setting['TO_FIT']:
                        interpolation_rings.append(ring_num)
                    if ring_num in processed:
                        continue
                    if ring_setting['TO_FIT']:
                        fit_block = {'Parameter': parameter}
                        if ring_setting['GROUP'][0] == ring_setting['GROUP'][1]:
                            fit_block['RINGS'] = f'{int(ring_setting["GROUP"][0])}'
                        else:
                            fit_block['RINGS'] = f'{int(ring_setting["GROUP"][1])}:{int(ring_setting["GROUP"][0])}'
                        for i in range(ring_setting['GROUP'][0], ring_setting['GROUP'][1] + 1):
                            processed.append(i)
                        print(processed, ring_num, ring_setting['GROUP'])
                        if not ring_setting['BLOCK_FIT'] and ring_setting['GROUP'][0] != ring_setting['GROUP'][1]:
                            fit_block['Parameter'] = f'!{parameter}'
                        for keys in owner.fitting_parameters:
                            if keys in ['VARY', 'VARINDX']:
                                pass
                            else:
                                if ring_setting[keys] is not None:
                                    fit_block[keys] = ring_setting[keys]
                                else:
                                    fit_block[keys] = parValsFitSetting[keys]
                        fitting_blocks.append(fit_block)
                    else:
                        processed.append(ring_num)
                for block in fitting_blocks:
                    owner.Tirific_Template['VARY'] += f' {block["Parameter"]} {block["RINGS"]},'
                    for keys in owner.fitting_parameters:
                        if keys in ['VARY', 'VARINDX']:
                            pass
                        else:
                            if block[keys] is None:
                                owner.Tirific_Template[keys] += ' '
                            else:
                                if isinstance(block[keys], int):
                                    owner.Tirific_Template[keys] += f'{int(block[keys])} '
                                else:
                                    owner.Tirific_Template[keys] += f'{block[keys]:{precision}} '

                if len(interpolation_rings) > 0:
                    owner.Tirific_Template['VARINDX'] += f' {parameter} {" ".join([f"{x}" for x in interpolation_rings])}'
        if owner.Tirific_Template['VARY'].endswith(','):
            owner.Tirific_Template['VARY'] = owner.Tirific_Template['VARY'][:-1]
        for key in owner.fitting_parameters:
            print(owner.Tirific_Template[key])
        print("Fitting settings updated in template. Superweird")
