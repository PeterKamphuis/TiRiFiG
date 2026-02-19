def main():
    print("Welcome to TiRiFiG Launcher!")
    # Additional launcher code would go here
 
    #try:
    from PyQt6 import QtWidgets, QtCore
    print("PyQt6 is available. Launching GUI...")

    from TiRiFiG.qt6_launcher import main as main_qt6
    main_qt6()
    return
        # Code to launch the GUI would go here
    #except ImportError:
    #    pass
   
    try:
        from PyQt5 import QtWidgets, QtCore
        print("PyQt5 is available. Launching GUI...")
        from TiRiFiG.qt5_launcher import main as main_qt5
        main_qt5()
        return
        # Code to launch the GUI would go here
    except ImportError:
        pass
     
    try:
        from PyQt4 import QtGui, QtCore
        print("PyQt4 is available. but the launcher is not up to date")
       
        from TiRiFiG.qt4_launcher import main as main_qt4
        main_qt4()
        return
        # Code to launch the GUI would go here
    except ImportError:
        pass
    
    print("No compatible PyQt version found. Please install PyQt5.")
if __name__ == "__main__":
    main()