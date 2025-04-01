# Improved LotusUIManager.py
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
                             QMessageBox, QPushButton, QSplitter, QStackedWidget, QMainWindow)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from src.Views.LotusToolbar import LotusToolbar
from src.Views.LotusHeader import LotusHeader
from src.Services.LotusConfig import LotusConfig
import os


class LotusUIManager(QObject):
    # tab signals
    insertRequested = pyqtSignal()
    editRequested = pyqtSignal()
    deleteRequested = pyqtSignal()
    undoRequested = pyqtSignal()
    redoRequested = pyqtSignal()
    saveRequested = pyqtSignal()
    # toolbar signals
    exitRequested = pyqtSignal()
    saveAllRequested = pyqtSignal()
    toggleThemeRequested = pyqtSignal()
    shortcutsHelpRequested = pyqtSignal()
    # tab change signal
    tabChanged = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.toolbar = LotusToolbar()
        self.main_splitter = None
        self.tabs = None
        self.header = None
        self.right_panel = None

    def setup_main_window(self, window_title, icon, geometry):
        """Set up the main window properties"""
        self.parent.setWindowTitle(window_title)
        self.parent.setWindowIcon(icon)
        self.parent.setGeometry(*geometry)
        self.parent.addToolBar(self.toolbar)

    def create_main_layout(self, af_dcfg_file, mutex_file):
        """Create the main layout with splitter and panels"""
        # Main layout
        main_layout = QHBoxLayout()

        # Create splitter
        self.main_splitter = QSplitter(Qt.Horizontal)

        # Create left panel with tabs
        left_panel = self.create_left_panel(af_dcfg_file)

        # Create right panel stack
        self.right_panel = QStackedWidget()

        # Add panels to splitter
        self.main_splitter.addWidget(left_panel)
        self.main_splitter.addWidget(self.right_panel)
        self.main_splitter.setSizes([400, 600])  # Initial size distribution

        main_layout.addWidget(self.main_splitter)

        # Set up central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.parent.setCentralWidget(central_widget)

        return main_layout

    def create_left_panel(self, file):
        """Create the left panel with header, tabs and buttons"""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        # header
        self.header = LotusHeader(os.getcwd(), file)
        left_layout.addWidget(self.header)
        # tabs
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.tabChanged.emit)
        left_layout.addWidget(self.tabs)
        # buttons
        buttons_layout = self._create_buttons_layout()
        left_layout.addLayout(buttons_layout)

        return left_panel

    def _create_buttons_layout(self):
        """Create a layout with buttons for the left panel."""
        self.buttons_layout = QHBoxLayout()

        self.insert_line_button = QPushButton("Insert")
        self.insert_line_button.setIcon(LotusConfig.get_icon("INSERT_LINE"))
        self.insert_line_button.setShortcut(QKeySequence("Ctrl+I"))
        self.buttons_layout.addWidget(self.insert_line_button)

        self.enable_edit_button = QPushButton("Edit")
        self.enable_edit_button.setIcon(LotusConfig.get_icon("ENABLE_EDIT"))
        self.enable_edit_button.setShortcut(QKeySequence("Ctrl+E"))
        self.buttons_layout.addWidget(self.enable_edit_button)

        self.delete_line_button = QPushButton("Delete")
        self.delete_line_button.setIcon(LotusConfig.get_icon("ERASE"))
        self.delete_line_button.setShortcut(QKeySequence.Delete)
        self.buttons_layout.addWidget(self.delete_line_button)

        self.undo_button = QPushButton("Undo")
        self.undo_button.setIcon(LotusConfig.get_icon("UNDO"))
        self.undo_button.setShortcut(QKeySequence.Undo)
        self.buttons_layout.addWidget(self.undo_button)

        self.redo_button = QPushButton("Redo")
        self.redo_button.setIcon(LotusConfig.get_icon("REDO"))
        self.redo_button.setShortcut(QKeySequence.Redo)
        self.buttons_layout.addWidget(self.redo_button)

        self.save_button = QPushButton("Save")
        self.save_button.setIcon(LotusConfig.get_icon("SAVE"))
        self.save_button.setShortcut(QKeySequence.Save)
        self.buttons_layout.addWidget(self.save_button)

        return self.buttons_layout

    def disable_buttons(self):
        self.insert_line_button.setEnabled(False)
        self.enable_edit_button.setEnabled(False)
        self.delete_line_button.setEnabled(False)
        self.undo_button.setEnabled(False)
        self.redo_button.setEnabled(False)
        self.save_button.setEnabled(False)

    def enable_buttons(self):
        self.insert_line_button.setEnabled(True)
        self.enable_edit_button.setEnabled(True)
        self.delete_line_button.setEnabled(True)
        self.undo_button.setEnabled(True)
        self.redo_button.setEnabled(True)
        self.save_button.setEnabled(True)
    def add_tab(self, widget, title):
        """Add a tab to the tab widget"""
        index = self.tabs.addTab(widget, title)
        return index

    def add_right_panel_content(self, widget):
        """Add a widget to the right panel stack"""
        index = self.right_panel.addWidget(widget)
        return index

    def update_header_filepath(self, filepath):
        """Update the header filepath"""
        self.header.change_filepath(filepath)

    def connect_signals(self):
        """Connect signals to their respective slots."""
        self.insert_line_button.clicked.connect(self.insertRequested.emit)
        self.enable_edit_button.clicked.connect(self.editRequested.emit)
        self.delete_line_button.clicked.connect(self.deleteRequested.emit)
        self.undo_button.clicked.connect(self.undoRequested.emit)
        self.redo_button.clicked.connect(self.redoRequested.emit)
        self.save_button.clicked.connect(self.saveRequested.emit)

        self.toolbar.exitApplication.connect(self.exitRequested.emit)
        self.toolbar.save_all_button.clicked.connect(self.saveAllRequested.emit)
        self.toolbar.toggle_theme_button.clicked.connect(self.toggleThemeRequested.emit)

    def show_info_message(self, title, message):
        """Show an information message box."""
        QMessageBox.information(self.parent, title, message)

    def show_warning_message(self, title, message):
        """Show a warning message box."""
        QMessageBox.warning(self.parent, title, message)

    def show_question_message(self, title, message, buttons):
        """Show a question message box with specified buttons."""
        return QMessageBox.question(self.parent, title, message, buttons)

    def get_current_tab_index(self):
        """Get the current tab index"""
        return self.tabs.currentIndex()

    def set_right_panel_current_index(self, index):
        """Set the current index of the right panel stack"""
        self.right_panel.setCurrentIndex(index)