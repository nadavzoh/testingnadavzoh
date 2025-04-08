from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget,
                             QDialogButtonBox)

from src.Views.AfDialogView import AfDialogView
from src.Views.MutexDialogView import MutexDialogView
from src.Views.CommentTabView import CommentTabView

"""CHANGE CLASS TO GENERIC BASE AbstractDialogView"""
class BaseDialogView(QWidget):  # change to qwidget

    def __init__(self, parent=None, tab_type="af"):
        super().__init__(parent)
        self.setGeometry(1100, 200, 800, 800)
        self._setup_ui(tab_type)

    # todo: fix this so that it is not hardcoded and accommodates different tabs
    def _setup_ui(self, tab_type="af"):
        """Set up the user interface components."""
        # Main layout
        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()
        #### REFACTOR ####
        if tab_type == "af":
            self.main_tab = AfDialogView()
            self.tabs.addTab(self.main_tab, "Pattern")
        elif tab_type == "mutex":
            # self.main_tab = QWidget()  # TODO: change when mutex dialog is implemented
            self.main_tab = MutexDialogView()
            self.tabs.addTab(self.main_tab, "Mutex")
        #### REFACTOR ####
        self.comment_tab = CommentTabView()
        self.tabs.addTab(self.comment_tab, "Comment")
        self.layout.addWidget(self.tabs)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Reset | QDialogButtonBox.Cancel, Qt.Horizontal)
        self.save_line_button = self.button_box.button(QDialogButtonBox.Save)
        self.reset_button = self.button_box.button(QDialogButtonBox.Reset)
        self.cancel_button = self.button_box.button(QDialogButtonBox.Cancel)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)


