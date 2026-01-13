def main():
    print("Welcome to TiRiFiG Launcher!")
    # Additional launcher code would go here
    executed = False
    try:
        from PyQt4 import QtGui, QtCore
        print("PyQt4 is available. Launching GUI...")
        executed = True
        from TiRiFiG.qt4_launcher import main as main_qt4
        main_qt4()
        # Code to launch the GUI would go here
    except ImportError:
        pass

    try:
        from PyQt5 import QtWidgets, QtCore
        print("PyQt5 is available. Launching GUI...")
        executed = True
        from TiRiFiG.qt5_launcher import main as main_qt5
        main_qt5()
        # Code to launch the GUI would go here
    except ImportError:
        pass
    
    if not executed:
        print("No compatible PyQt version found. Please install PyQt4 or PyQt5.")
if __name__ == "__main__":
    main()