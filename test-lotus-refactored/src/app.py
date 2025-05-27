#!/usr/intel/pkgs/python3/3.11.1/bin/python3 -tt
"""Application entry point for the Lotus application."""

import sys
from PyQt5.QtWidgets import QApplication



def main():
    """
    Entry point for the Lotus application.
    
    Creates and shows the main window.
    
    Returns:
        int: Application exit code
    """
    app = QApplication(sys.argv)

    main_window = Lotus()
    main_window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())

