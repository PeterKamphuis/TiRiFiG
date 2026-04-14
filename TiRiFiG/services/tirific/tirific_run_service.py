"""Unified service for TiRiFiC run warnings, progress, and startup."""

import os
import pty
import re
import select
import subprocess

from PyQt6 import QtCore, QtWidgets


class TirificRunService:
    """Encapsulate MainWindow run-related behavior with unchanged semantics."""

    @staticmethod
    def _fit_block_count(owner):
        """Count fitting blocks from VARY entries used by TiRiFiC."""
        vary = str(owner.Tirific_Template.get('VARY', '')).strip()
        if not vary:
            return 1
        blocks = [block.strip() for block in vary.split(',') if block.strip()]
        return max(1, len(blocks))

    @staticmethod
    def _consume_progress_line(line, loops, fit_blocks, current_loop, current_block, last_p_marker):
        """Update loop/block progress state from a single TiRiFiC output line."""
        l_match = re.search(r'(?i)\bL:\s*([0-9]+)', line)
        if l_match:
            parsed_loop = int(l_match.group(1))
            parsed_loop = max(1, min(parsed_loop, loops))
            if parsed_loop != current_loop:
                current_loop = parsed_loop
                current_block = 0
                last_p_marker = None

        p_match = re.search(r'(?i)\bP:\s*([^\s,;]+)', line)
        if p_match:
            p_marker = p_match.group(1).strip()
            if p_marker.upper().startswith('GEN'):
                p_marker = None
            if p_marker and p_marker != last_p_marker:
                last_p_marker = p_marker
                current_block = min(current_block + 1, fit_blocks)

        finished = 'finish' in line.lower()
        completed = ((max(current_loop, 1) - 1) * fit_blocks) + current_block
        return current_loop, current_block, last_p_marker, completed, finished

    @staticmethod
    def show_run_warning(owner, message, message_box_cls):
        """Show the run warning dialog and keep existing return semantics."""
        if not message_box_cls.warning(owner, 'Run TiRiFiC Message', message):
            return False
        return True

    @staticmethod
    def run_progress(owner, cmd, message_box_cls, output_fd=None):
        """Show and update run progress dialog by parsing TiRiFiC process output."""
        progress = QtWidgets.QProgressDialog("Operation in progress...", "Cancel", 0, 100)
        stdout_line = "Waiting for TiRiFiC output..."
        loops = max(1, int(float(owner.Tirific_Template.get('LOOPS', 1))))
        fit_blocks = TirificRunService._fit_block_count(owner)
        total_steps = loops * fit_blocks
        progress.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        progress.setMaximum(total_steps)
        progress.setMinimumDuration(0)
        progress.resize(700, 130)
        current_loop = 1
        current_block = 0
        last_p_marker = None
        message = "Stopped"
        completed = 0
        status = 'running'
        canceled = False
        stream = cmd.stdout
        buffer = ""
        progress.setValue(0)
        progress.setLabelText(f"Operation in progress...\n{stdout_line}")
        progress.show()
        QtWidgets.QApplication.processEvents()

        while cmd.poll() is None and status == 'running':
            progress.setLabelText(f"Operation in progress...\n{stdout_line}")
            QtWidgets.QApplication.processEvents()
            if progress.wasCanceled():
                canceled = True
                cmd.kill()
                break

            if output_fd is not None:
                ready, _writeable, _errors = select.select([output_fd], [], [], 0.2)
                if not ready:
                    continue
                try:
                    chunk = os.read(output_fd, 4096)
                except OSError:
                    break
                if not chunk:
                    break

                buffer += chunk.decode(errors='replace')
                lines = buffer.splitlines(keepends=True)
                if lines and not lines[-1].endswith("\n"):
                    buffer = lines.pop()
                else:
                    buffer = ""

                for line in lines:
                    clean_line = line.rstrip("\r\n")
                    stdout_line = " ".join(clean_line.strip().split())
                    if not stdout_line:
                        stdout_line = "(blank output line)"
                    elif len(stdout_line) > 180:
                        stdout_line = stdout_line[:177] + "..."

                    current_loop, current_block, last_p_marker, completed, finished = TirificRunService._consume_progress_line(
                        clean_line, loops, fit_blocks, current_loop, current_block, last_p_marker
                    )
                    if finished:
                        status = 'finished'
                        message = clean_line.strip() or "Finished"
                        progress.setValue(total_steps)
                        break

                progress.setValue(min(total_steps, completed))
            else:
                line = ""
                if stream is not None:
                    ready, _writeable, _errors = select.select([stream], [], [], 0.2)
                    if ready:
                        line = stream.readline()

                if not line:
                    continue

                stdout_line = " ".join(line.strip().split())
                if not stdout_line:
                    stdout_line = "(blank output line)"
                elif len(stdout_line) > 180:
                    stdout_line = stdout_line[:177] + "..."

                current_loop, current_block, last_p_marker, completed, finished = TirificRunService._consume_progress_line(
                    line, loops, fit_blocks, current_loop, current_block, last_p_marker
                )
                if finished:
                    status = 'finished'
                    message = line.strip() or "Finished"
                    progress.setValue(total_steps)
                    break

                progress.setValue(min(total_steps, completed))

        if output_fd is not None and buffer and status == 'running':
            clean_line = buffer.rstrip("\r\n")
            if clean_line:
                stdout_line = " ".join(clean_line.strip().split())
                if not stdout_line:
                    stdout_line = "(blank output line)"
                elif len(stdout_line) > 180:
                    stdout_line = stdout_line[:177] + "..."
                current_loop, current_block, last_p_marker, completed, finished = TirificRunService._consume_progress_line(
                    clean_line, loops, fit_blocks, current_loop, current_block, last_p_marker
                )
                if finished:
                    status = 'finished'
                    message = clean_line.strip() or "Finished"

        if canceled:
            message = "Stopped"
        elif status != 'finished' and cmd.poll() == 0:
            message = "Finished"

        if canceled:
            progress.setValue(min(total_steps, completed))
        else:
            progress.setValue(total_steps)
        message_box_cls.information(owner, "Information", message)

    @staticmethod
    def start_run(owner, message_box_cls):
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
            master_fd = None
            slave_fd = None
            try:
                master_fd, slave_fd = pty.openpty()
                cmd = subprocess.Popen(
                    ["tirific", f"deffile={owner.fileName}"],
                    cwd=file_name_path,
                    stdout=slave_fd,
                    stderr=slave_fd,
                    stdin=subprocess.DEVNULL,
                    close_fds=True,
                )
                os.close(slave_fd)
                slave_fd = None

            except OSError:
                if slave_fd is not None:
                    os.close(slave_fd)
                if master_fd is not None:
                    os.close(master_fd)
                message_box_cls.information(
                    owner,
                    "Information",
                    "TiRiFiC is not installed or configured properly on system.",
                )
            else:
                try:
                    TirificRunService.run_progress(owner, cmd, message_box_cls, output_fd=master_fd)
                finally:
                    if master_fd is not None:
                        os.close(master_fd)
        else:
            owner.tirificMessage(
                "The input data cube specified in INSET ("
                + owner.Tirific_Template['INSET']
                + ") parameter is not available."
            )
