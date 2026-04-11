"""Unified service for TiRiFiC run warnings, progress, and startup."""

import os
import time

from PyQt6 import QtCore, QtWidgets


class TirificRunService:
    """Encapsulate MainWindow run-related behavior with unchanged semantics."""

    @staticmethod
    def show_run_warning(owner, message, message_box_cls):
        """Show the run warning dialog and keep existing return semantics."""
        if not message_box_cls.warning(owner, 'Run TiRiFiC Message', message):
            return False
        return True

    @staticmethod
    def run_progress(owner, cmd, message_box_cls):
        """Show and update run progress dialog until command completes/cancels."""
        progress = QtWidgets.QProgressDialog("Operation in progress...", "Cancel", 0, 100)
        progress.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        progress.setMaximum(int(float(owner.Tirific_Template['LOOPS']) * 1e6))
        progress.resize(500, 100)
        prev = 1
        message = "Stopped"
        completed = int(prev * 1e6) / 2
        status = 'running'
        progress.show()
        time.sleep(10)
        while cmd.poll() is None and status == 'running':
            with open(owner.progressPath, 'r') as progress_file:
                data = progress_file.readlines()
                for line in data:
                    values = line.split(" ")
                    if 'L:' in values[0].upper():
                        count = values[0].split(":")
                        count = count[1].split("/")
                        if int(float(count[0])) > prev:
                            if int(float(count[0])) == int(float(owner.Tirific_Template['LOOPS'])):
                                completed += 0.0001
                            else:
                                prev = int(float(count[0]))
                                completed = prev * 1e6
                        else:
                            completed += 0.0001
                    elif "finish" in values[0].lower():
                        status = 'finished'
                        progress.setValue(int(float(owner.Tirific_Template['LOOPS'])) * 1e6)
                        message = line
                        break
            progress.setValue(completed)
            if progress.wasCanceled():
                cmd.kill()
                break
        progress.setValue(int(float(owner.Tirific_Template['LOOPS'])) * 1e6)
        message_box_cls.information(owner, "Information", message)

    @staticmethod
    def start_run(owner, run_callable, message_box_cls):
        """Execute TiRiFiC run flow and user confirmations."""
        opened_file_name = getattr(owner, 'openedfileName', getattr(owner, 'openedfilename', ''))
        old_output_name = os.path.basename(owner.fileName)
        used_save_as = False

        if owner.fileName == opened_file_name:
            if not owner.tirificMessage(
                "The current setting will overwrite the original input .def file "
                f"({opened_file_name}).\n"
                "Press OK to choose a file name now via Save As, or Cancel to abort the run."
            ):
                return
            owner.saveAsAll()
            used_save_as = True

        file_name_path, file_name = os.path.split(owner.fileName)
        checked_names = {old_output_name, file_name}
        if owner.Tirific_Template['TIRDEF'] in checked_names:
            if not owner.tirificMessage(
                "This TiRiFiC run may overwrite the .def referenced by TIRDEF "
                f"({owner.Tirific_Template['TIRDEF']}).\n"
                f"Checked output names: old={old_output_name}, current={file_name}. Continue?"
            ):
                return

        fits_file_path = file_name_path + "/" + owner.Tirific_Template['INSET']
        if os.path.isfile(fits_file_path):
            if not used_save_as:
                owner.saveAll()
            try:
                cmd = run_callable(["tirific", f"deffile={owner.fileName}"], cwd=file_name_path)
            except OSError:
                message_box_cls.information(
                    owner,
                    "Information",
                    "TiRiFiC is not installed or configured properly on system.",
                )
            else:
                # Progress flow intentionally unchanged from current launcher behavior.
                del cmd
        else:
            owner.tirificMessage(
                "The input data cube specified in INSET ("
                + owner.Tirific_Template['INSET']
                + ") parameter is not available."
            )
