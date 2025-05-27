#!/usr/intel/pkgs/python3/3.11.1/bin/python3 -tt

import sys
from app import Lotus
from services.lotus_utils import create_splash_screen
from PyQt5.QtWidgets import QApplication


def main():
    """
    Entry point for the Lotus application.
    
    Initializes the application, shows a splash screen,
    creates the main window, and starts the event loop.
    """
    app = QApplication(sys.argv)
    splash = create_splash_screen(app)

    app.processEvents()
    main_window = Lotus()
    main_window.show()
    splash.finish(main_window)  # Close splash screen when main window is shown
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())

