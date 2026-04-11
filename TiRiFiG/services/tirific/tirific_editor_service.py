"""Service helpers for opening and syncing external text editor workflows."""

import os


class TirificEditorService:
    """Encapsulate MainWindow.openEditor behavior with unchanged flow."""

    @staticmethod
    def open_editor(owner, qt_widgets, run_callable, message_box_cls, timer_thread_cls):
        """Open configured editor or start sync timer fallback."""
        text, ok = qt_widgets.QInputDialog.getText(
            owner,
            "Text Editor Input Dialog",
            "Enter text editor:",
        )
        if ok:
            path, _name = os.path.split(owner.fileName)
            owner.tmpDeffile = os.path.join(path, "TiRiFiG_temp.def")
            owner.saveAsAll(owner.tmpDeffile)

            if text:
                program_name = str(text)
                try:
                    run_callable([program_name, owner.tmpDeffile])
                except OSError:
                    message_box_cls.information(
                        owner,
                        "Information",
                        "{} is not installed or configuredproperly on this system.".format(program_name),
                    )
            else:
                # Assign current modified time of temporary def file to before.
                owner.before = os.stat(owner.tmpDeffile).st_mtime
                owner.t = timer_thread_cls(1, owner.animate)
                owner.t.start()
