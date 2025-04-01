from PyQt5.QtWidgets import QPushButton, QToolBar, QMessageBox, QListView, QDialog, QVBoxLayout, QDialogButtonBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QKeySequence
from PyQt5.QtCore import pyqtSignal
from src.Services.LotusConfig import LotusConfig
class LotusToolbar(QToolBar):
    exitApplication = pyqtSignal()
    toggleTheme = pyqtSignal()
    def __init__(self):
        super().__init__()

        self.exit_button = QPushButton("Exit", self)
        self.exit_button.setIcon(LotusConfig.get_icon("CANCEL"))
        self.exit_button.clicked.connect(self.confirm_exit)
        self.exit_button.setShortcut(QKeySequence.Quit)
        self.addWidget(self.exit_button)

        self.save_all_button = QPushButton("Save All")
        self.save_all_button.setIcon(LotusConfig.get_icon("SAVE"))
        self.save_all_button.clicked.connect(lambda: print("TO IMPLEMENT: Save all files"))
        self.save_all_button.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.addWidget(self.save_all_button)

        self.toggle_theme_button = QPushButton("Toggle Dark/Light Mode")
        self.toggle_theme_button.setIcon(LotusConfig.get_icon("TOGGLE_THEME"))
        self.toggle_theme_button.setShortcut(QKeySequence("Ctrl+T"))
        self.addWidget(self.toggle_theme_button)

        self.shortcuts_helped_button = QPushButton("Help")
        self.shortcuts_helped_button.setShortcut(QKeySequence("Ctrl+H"))
        self.shortcuts_helped_button.clicked.connect(self.show_shortcuts)
        self.addWidget(self.shortcuts_helped_button)


    def confirm_exit(self):
        """Prompt the user to confirm before exiting the application."""
        reply = QMessageBox.question(self, "Exit Application", "Are you sure you want to exit?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.exitApplication.emit()


    def show_shortcuts(self):
        # Create the QListView and the model to store the shortcuts
        shortcut_list = QListView(self)
        shortcut_list_model = QStandardItemModel()
        shortcut_list.setModel(shortcut_list_model)

        # Define the list of shortcuts and actions
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
        # Add items to the model
        for action, shortcut in shortcuts:
            item = QStandardItem(f"{action}: {shortcut}")
            item.setEditable(False)  # Make the items non-editable
            shortcut_list_model.appendRow(item)

        # Create a custom dialog to display the shortcuts in a QListView
        dialog = QDialog(self)
        dialog.setWindowTitle("Shortcuts Help")
        dialog.setWindowIcon(LotusConfig.get_icon("LOTUS"))  # Set your desired icon here
        dialog.setMinimumWidth(400)
        dialog.setGeometry(300, 200, 400, 400)

        # Create a layout and add the QListView to it
        layout = QVBoxLayout(dialog)
        layout.addWidget(shortcut_list)

        # Add a button to close the dialog
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        # Show the dialog
        dialog.exec_()
