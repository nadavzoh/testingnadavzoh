from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QMessageBox, QDialog,
                             QPushButton, QSplitter, QStackedWidget, QDialogButtonBox, QListView,
                             QFileDialog)
from PyQt5.QtGui import QKeySequence, QStandardItemModel, QStandardItem
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from widgets.lotus_header import LotusHeader
from services.lotus_config import LotusConfig

import os


class LotusUIManager(QObject):
    """
    Manager for the Lotus application user interface.

    This class creates and manages the application's UI components, handles their
    layout, connects signals, and provides methods to update UI state. It serves as
    the central point for UI coordination and organization.

    Signals:
        insertRequested: Emitted when the user requests a line insertion
        editRequested: Emitted when the user requests to edit a line
        deleteRequested: Emitted when the user requests to delete a line
        undoRequested: Emitted when the user requests to undo an action
        redoRequested: Emitted when the user requests to redo an action
        saveRequested: Emitted when the user requests to save the current file
        exitRequested: Emitted when the user requests to exit the application
        saveAllRequested: Emitted when the user requests to save all files
        toggleThemeRequested: Emitted when the user requests to toggle theme
        tabChanged(int): Emitted when the user changes tabs, with the new tab index

    Attributes:
        parent: Parent widget (main window)
        main_splitter (QSplitter): Main horizontal splitter
        tabs (QTabWidget): Tab widget for left panel
        header (LotusHeader): Header widget showing current file path
        right_panel (QStackedWidget): Right panel stacked widget
    """
    # tab signals
    insertRequested = pyqtSignal()
    editRequested = pyqtSignal()
    deleteRequested = pyqtSignal()
    undoRequested = pyqtSignal()
    redoRequested = pyqtSignal()
    saveRequested = pyqtSignal()
    # menu signals
    exitRequested = pyqtSignal()
    saveAsRequested = pyqtSignal()
    saveAllRequested = pyqtSignal()
    toggleThemeRequested = pyqtSignal()
    # fone size adjustment
    increaseFontSizeRequested = pyqtSignal()
    decreaseFontSizeRequested = pyqtSignal()
    resetFontSizeRequested = pyqtSignal()
    # tab change signal
    tabChanged = pyqtSignal(int)

    def __init__(self, parent):
        """
        Initialize the UI manager.

        Args:
            parent: Parent widget (main window)
        """
        super().__init__()
        self.parent = parent
        self.main_splitter = None
        self.tabs = None
        self.header = None
        self.right_panel = None

    def setup_main_window(self, window_title, icon, geometry=None):
        """
        Set up the main window properties.

        Args:
            window_title (str): Title for the main window
            icon (QIcon): Icon for the main window
            geometry (tuple, optional): Window geometry (x, y, width, height)
        """
        self.parent.setWindowTitle(window_title)
        self.parent.setWindowIcon(icon)
        if geometry:
            self.parent.setGeometry(*geometry)

    def create_main_layout(self):
        """
        Create the main layout with splitter and panels.

        Returns:
            QHBoxLayout: The main layout object
        """
        main_layout = QHBoxLayout()

        self.main_splitter = QSplitter(Qt.Horizontal)
        left_panel = self.create_left_panel()  # not so pretty, workaround.
        self.right_panel = QStackedWidget()

        self.main_splitter.addWidget(left_panel)
        self.main_splitter.addWidget(self.right_panel)
        self.main_splitter.setSizes([500, 500])

        main_layout.addWidget(self.main_splitter)

        # Set up central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.parent.setCentralWidget(central_widget)

        return main_layout

    def create_left_panel(self):
        """
        Create the left panel with header, tabs and buttons.

        Returns:
            QWidget: The configured left panel widget
        """
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        # header
        self.header = LotusHeader()
        left_layout.addWidget(self.header)
        # tabs
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.tabChanged.emit)
        left_layout.addWidget(self.tabs)
        # buttons
        buttons_layout = self._create_buttons_layout()
        left_layout.addLayout(buttons_layout)

        return left_panel

    def _create_button(self, text, icon, shortcut, enabled=True):
        """
        Create a button with specified text, icon and shortcut.

        Args:
            text (str): Button label text
            icon (str): Icon name to use from LotusConfig
            shortcut (str): Keyboard shortcut for the button
            enabled (bool, optional): Whether button is initially enabled

        Returns:
            QPushButton: The configured button
        """
        button = QPushButton(text)
        button.setIcon(LotusConfig.get_icon(icon))
        button.setShortcut(QKeySequence(shortcut))
        button.setEnabled(enabled)
        return button

    def _create_buttons_layout(self):
        """
        Create a layout with buttons for the left panel.

        Creates and configures all the action buttons for the document interface.

        Returns:
            QHBoxLayout: Layout containing the action buttons
        """
        self.buttons_layout = QHBoxLayout()

        self.insert_line_button = self._create_button("Insert", "INSERT_LINE", "Ctrl+I")
        self.buttons_layout.addWidget(self.insert_line_button)

        self.enable_edit_button = self._create_button("Edit", "ENABLE_EDIT", "Ctrl+E")
        self.buttons_layout.addWidget(self.enable_edit_button)

        self.delete_line_button = self._create_button("Delete", "ERASE", "Delete")
        self.buttons_layout.addWidget(self.delete_line_button)

        return self.buttons_layout

    def disable_buttons(self):
        """
        Disable all action buttons and tabs.

        Used when no document is active or operations should be prevented.
        """
        self.insert_line_button.setEnabled(False)
        self.enable_edit_button.setEnabled(False)
        self.delete_line_button.setEnabled(False)
        self.tabs.setEnabled(False)

    def enable_buttons(self):
        """
        Enable all action buttons and tabs.

        Used when a document is active and operations should be available.
        """
        self.insert_line_button.setEnabled(True)
        self.enable_edit_button.setEnabled(True)
        self.delete_line_button.setEnabled(True)
        self.tabs.setEnabled(True)

    def add_tab_to_left_panel(self, widget, title):
        """
        Add a tab to the tab widget.

        Args:
            widget (QWidget): The widget to add as a tab
            title (str): The title for the tab

        Returns:
            int: Index of the newly added tab
        """
        index = self.tabs.addTab(widget, title)
        return index

    def add_right_panel_content(self, widget):
        """
        Add a widget to the right panel stack.

        Args:
            widget (QWidget): The widget to add to the right panel

        Returns:
            int: Index of the newly added widget in the stack
        """
        index = self.right_panel.addWidget(widget)
        return index

    def update_header_filepath(self, filepath):
        """
        Update the header filepath.

        Args:
            filepath (str): The path to display in the header
        """
        self.header.change_filepath(filepath)

    def connect_signals(self):
        """
        Connect signals to their respective slots.

        Sets up all signal connections between UI elements and their handlers.
        """
        self.insert_line_button.clicked.connect(self.insertRequested.emit)
        self.enable_edit_button.clicked.connect(self.editRequested.emit)
        self.delete_line_button.clicked.connect(self.deleteRequested.emit)

    def show_info_message(self, title, message):
        """
        Show an information message box.

        Args:
            title (str): Title of the message box
            message (str): Message to display
        """
        QMessageBox.information(self.parent, title, message)

    def show_warning_message(self, title, message):
        """
        Show a warning message box.

        Args:
            title (str): Title of the message box
            message (str): Warning message to display
        """
        QMessageBox.warning(self.parent, title, message)

    def show_question_message(self, title, message, buttons):
        """
        Show a question message box with specified buttons.

        Args:
            title (str): Title of the message box
            message (str): Question to display
            buttons: Button flags to include (e.g., QMessageBox.Yes | QMessageBox.No)

        Returns:
            int: ID of the button that was clicked
        """
        return QMessageBox.question(self.parent, title, message, buttons)

    def get_current_tab_index(self):
        """
        Get the current tab index.

        Returns:
            int: Index of the currently selected tab
        """
        return self.tabs.currentIndex()

    def set_right_panel_current_index(self, index):
        """
        Set the current index of the right panel stack.

        Args:
            index (int): Index of the widget to show
        """
        self.right_panel.setCurrentIndex(index)

    def _confirm_exit(self):
        """
        Show confirmation dialog before exiting the application.

        If the user confirms, emits the exitRequested signal.
        """
        reply = self.show_question_message(
            "Exit Application",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.exitRequested.emit()

    def show_save_as_dialog(self):
        """
        Show a file dialog for 'Save As' functionality.
        
        Opens a file dialog starting in LOTUS_USER_WARD directory (if available)
        allowing the user to choose a new save location.
        
        Returns:
            str: Selected file path or empty string if canceled
        """
        start_dir = os.environ.get('LOTUS_USER_WARD', os.path.expanduser('~'))
        
        # Show the file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Save File As",
            start_dir,
            "All Files (*);;DCFG Files (*.dcfg);;Text Files (*.txt)"
        )
            
        return file_path

    @staticmethod
    def show_shortcuts():
        """
        Show the keyboard shortcuts help dialog.

        Displays a dialog with a list of all available keyboard shortcuts
        in the application.
        """
        shortcut_list = QListView()
        shortcut_list_model = QStandardItemModel()
        shortcut_list.setModel(shortcut_list_model)
        shortcuts = [
            ("Shortcuts Help", "Ctrl+H"),
            ("Exit", "Ctrl+Q"),
            ("Save File", "Ctrl+S"),
            ("Save As", "Ctrl+Alt+S"),
            ("Save All", "Ctrl+Shift+S"),
            ("Undo", "Ctrl+Z"),
            ("Redo", "Ctrl+Shift+Z"),
            ("Toggle Dark/Light Mode", "Ctrl+T"),
            ("Increase Font Size", "Ctrl+="),
            ("Decrease Font Size", "Ctrl+-"),
            ("Reset Font Size", "Ctrl+0"),
            ("Insert New Line", "Ctrl+I"),
            ("Edit Line", "Ctrl+E"),
            ("Delete Line", "Delete"),
            ("Unselect Line", "Esc"),
            ("Comment/Uncomment Line", "Ctrl+/"),
            ("Duplicate Line", "Ctrl+D"),
            ("Move Line Up", "Alt+↑"),
            ("Move Line Down", "Alt+↓"),
            ("Update Results", "Enter"),
            ("Search Results", "Ctrl+F"),
            ("Cancel Dialog", "Esc"),
            ("Save Line", "Ctrl+Shift+E"),
            ("Reset Dialog", "Ctrl+R")
        ]
        for action, shortcut in shortcuts:
            item = QStandardItem(f"{action}: {shortcut}")
            item.setEditable(False)
            shortcut_list_model.appendRow(item)

        dialog = QDialog()
        dialog.setWindowTitle("Shortcuts Help")
        dialog.setWindowIcon(LotusConfig.get_icon("LOTUS"))
        dialog.setMinimumWidth(400)
        dialog.setGeometry(300, 200, 400, 700)

        layout = QVBoxLayout(dialog)
        layout.addWidget(shortcut_list)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.exec_()