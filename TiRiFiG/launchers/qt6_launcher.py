# -*- coding: UTF-8 -*-
#########################################################################################
# Author: Samuel (samueltwum1@gmail.com) with MSc supervisors                           #
# Copyright 2018 Samuel N. Twum                                                         #
#                                                                                       #
# GPL license - see LICENSE.txt for details                                             #
#########################################################################################

"""Qt6 launcher entrypoint.

This module initializes styling, creates the Qt application, and starts
`MainWindow` from `TiRiFiG.services.main_window.main_window`.
"""

import logging
import os
import sys
import warnings

os.environ["QT_API"] = "pyqt6"

# Suppress Qt painting-related warnings from matplotlib blitting
warnings.filterwarnings("ignore", message=".*Recursive repaint detected.*")
warnings.filterwarnings("ignore", message=".*Paint device returned engine.*")
warnings.filterwarnings("ignore", message=".*Painter not active.*")

import matplotlib
matplotlib.use("qt5agg")
from matplotlib import style
  
style.use("seaborn-v0_8")
from PyQt6 import QtGui, QtWidgets
from TiRiFiG.services.style.modern_style_service import ModernStyleService
from TiRiFiG.services.main_window.main_window import MainWindow


try:
    from importlib.resources import files as import_pack_files
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    # For Py<3.9 files is not available
    from importlib_resources import files as import_pack_files
    
def logWarnings():
    # logging.captureWarnings(True)
    # logging.basicConfig(filename='test.log', format='%(asctime)s %(name)s %(levelname)s %(message)s',
    #                     datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logger = logging.getLogger(__name__)
    # warnings_logger = logging.getLogger("py.warnings")

    formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logger_file_handler = logging.FileHandler('TiRiFiG.log', mode='a')
    logger_file_handler.setFormatter(formatter)

    logger.addHandler(logger_file_handler)
    # warnings_logger.addHandler(logger_file_handler)
    # logger.setLevel(logging.DEBUG)
    # warnings_logger.setLevel(logging.DEBUG)

def main():
    # Suppress Qt painting-related warnings from matplotlib blitting
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = ''
    
    logWarnings()
    if os.path.isfile(os.getcwd() + "/tmpDeffile.def"):
        os.remove(os.getcwd() + "/tmpDeffile.def")

    app = QtWidgets.QApplication(sys.argv)
    # Apply modern style (set a background image path if desired)
    background_image_path =  str(import_pack_files('TiRiFiG.utilities.background')/'Background.png')  # e.g., "path/to/your/image.png"
    try:
        ModernStyleService.apply_modern_style(
            app,
            QtWidgets,
            QtGui,
            background_image_path=background_image_path,
        )
    except Exception as _e:
        # Non-fatal if styling fails
        pass
    GUI = MainWindow()
    GUI.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
