from PyQt5.QtWidgets import (QMainWindow, QMessageBox)
from PyQt5.QtGui import QCloseEvent
from managers.lotus_action_manager import LotusActionManager
from managers.lotus_file_manager import LotusFileManager
from managers.lotus_tab_manager import LotusTabManager
from managers.lotus_theme_manager import LotusThemeManager
from managers.lotus_ui_manager import LotusUIManager
from managers.lotus_menu_manager import LotusMenuManager
from services.lotus_config import LotusConfig


class Lotus(QMainWindow):
    """
    Main application window for the Lotus application.
    
    This class serves as the entry point for the application UI and
    coordinates between different managers and controllers.
    """
    
    def __init__(self):
        super().__init__()
        self._files_manager = LotusFileManager()
        self._theme_manager = LotusThemeManager()
        self._ui_manager = LotusUIManager(self)
        self._menu_manager = LotusMenuManager(self, self._ui_manager)
        self._tab_manager = LotusTabManager(self._ui_manager, self._files_manager)
        self._action_controller = LotusActionManager(self._tab_manager, self._ui_manager)
        self._setup_ui()
        self._setup_tabs()
        self._connect_signals()

    def _setup_ui(self):
        self._ui_manager.setup_main_window(
            self.__class__.__name__,
            LotusConfig.get_icon("LOTUS")
        )
        self._ui_manager.create_main_layout()
        self.showMaximized()

    def _setup_tabs(self):
        self._tab_manager.initialize_tabs()

    def _connect_signals(self):
        self._ui_manager.connect_signals()
        self._ui_manager.exitRequested.connect(self.close)

    def closeEvent(self, a0):
        # Check if any tab has unsaved changes
        has_changes = self._action_controller.check_for_unsaved_changes()
        if has_changes:
            reply = self._ui_manager.show_question_message(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before quitting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            if reply == QMessageBox.Save:
                # Trigger save all action
                self._ui_manager.saveAllRequested.emit()
            elif reply == QMessageBox.Cancel:
                if isinstance(a0, QCloseEvent):
                    a0.ignore()
                return
        if isinstance(a0, QCloseEvent):
            a0.accept()