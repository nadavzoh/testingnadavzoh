from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QPushButton, QToolBar

from src.Services.LotusConfig import LotusConfig


class LotusToolbar(QToolBar):
    exitClicked = pyqtSignal()
    saveAll = pyqtSignal()
    toggleTheme = pyqtSignal()
    showShortcuts = pyqtSignal()
    def __init__(self):
        super().__init__()

        self.exit_button = QPushButton("Exit", self)
        self.exit_button.setIcon(LotusConfig.get_icon("CANCEL"))
        self.exit_button.setShortcut(QKeySequence.Quit)
        self.exit_button.clicked.connect(self.exitClicked.emit)
        self.addWidget(self.exit_button)

        self.save_all_button = QPushButton("Save All")
        self.save_all_button.setIcon(LotusConfig.get_icon("SAVE"))
        self.save_all_button.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.save_all_button.clicked.connect(self.saveAll.emit)
        self.addWidget(self.save_all_button)

        self.toggle_theme_button = QPushButton("Toggle Dark/Light Mode")
        self.toggle_theme_button.setIcon(LotusConfig.get_icon("TOGGLE_THEME"))
        self.toggle_theme_button.setShortcut(QKeySequence("Ctrl+T"))
        self.toggle_theme_button.clicked.connect(self.toggleTheme.emit)
        self.addWidget(self.toggle_theme_button)

        self.shortcuts_helped_button = QPushButton("Help")
        self.shortcuts_helped_button.setShortcut(QKeySequence("Ctrl+H"))
        self.shortcuts_helped_button.clicked.connect(self.showShortcuts.emit)
        self.addWidget(self.shortcuts_helped_button)
