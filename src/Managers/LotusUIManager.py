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
        main_layout = QHBoxLayout()

        self.main_splitter = QSplitter(Qt.Horizontal)
        left_panel = self.create_left_panel(default_tab_file=af_dcfg_file)  # not so pretty, workaround.
        self.right_panel = QStackedWidget()

        self.main_splitter.addWidget(left_panel)
        self.main_splitter.addWidget(self.right_panel)
        self.main_splitter.setSizes([400, 600])

        main_layout.addWidget(self.main_splitter)

        # Set up central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.parent.setCentralWidget(central_widget)

        return main_layout

    def create_left_panel(self, default_tab_file):
        """Create the left panel with header, tabs and buttons"""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        # header
        self.header = LotusHeader(default_tab_file)
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

        # TODO: disbale by default, enable when a line is selected
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

        self.toolbar.exitClicked.connect(self._confirm_exit)
        self.toolbar.saveAll.connect(self.saveAllRequested.emit)
        self.toolbar.toggleTheme.connect(self.toggleThemeRequested.emit)
        self.toolbar.showShortcuts.connect(self._show_shortcuts)

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

    def _confirm_exit(self):
        reply = self.show_question_message(
            "Exit Application",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.exitRequested.emit()

    def _show_shortcuts(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QListView
        from PyQt5.QtGui import QStandardItemModel, QStandardItem
        shortcut_list = QListView()
        shortcut_list_model = QStandardItemModel()
        shortcut_list.setModel(shortcut_list_model)
        shortcuts = [
            ("Exit", "Ctrl+Q"),
            ("Save All", "Ctrl+Shift+S"),
            ("Toggle Dark/Light Mode", "Ctrl+T"),
            ("Shortcuts Help", "Ctrl+H"),
            ("Save File", "Ctrl+S"),
            ("Insert New Line", "Ctrl+I"),
            ("Edit Line", "Ctrl+E"),
            ("Delete Line", "Delete"),
            ("Undo", "Ctrl+Z"),
            ("Redo", "Ctrl+Shift+Z"),
        ]
        for action, shortcut in shortcuts:
            item = QStandardItem(f"{action}: {shortcut}")
            item.setEditable(False)
            shortcut_list_model.appendRow(item)

        dialog = QDialog()
        dialog.setWindowTitle("Shortcuts Help")
        dialog.setWindowIcon(LotusConfig.get_icon("LOTUS"))
        dialog.setMinimumWidth(400)
        dialog.setGeometry(300, 200, 400, 400)

        layout = QVBoxLayout(dialog)
        layout.addWidget(shortcut_list)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.exec_()