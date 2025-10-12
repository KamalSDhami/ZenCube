#!/usr/bin/env python3
"""
ZenCube - Sandbox Manager GUI
Main application entry point
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow


def main():
    """Main application function"""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("ZenCube")
    app.setOrganizationName("ZenCube")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
