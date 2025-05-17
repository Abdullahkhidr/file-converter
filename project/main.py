#!/usr/bin/env python3
import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from project.gui.main_window import MainWindow
from project.utils.error_handler import ErrorHandler


def main():
    """Main entry point for the application."""
    # Set up logging
    ErrorHandler.setup_logging()
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("File Converter")
    app.setOrganizationName("File Converter")
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 