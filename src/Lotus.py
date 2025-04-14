from PyQt5.QtWidgets import (QMainWindow, QMessageBox)
from src.Managers.LotusActionManager import LotusActionManager
from src.Managers.LotusFilesManager import LotusFilesManager
from src.Managers.LotusTabManager import LotusTabManager
from src.Managers.LotusThemeManager import LotusThemeManager
from src.Managers.LotusUIManager import LotusUIManager
from src.Services.LotusConfig import LotusConfig


class Lotus(QMainWindow):
    def __init__(self):
        super().__init__()
        self._files_manager = LotusFilesManager()
        self._theme_manager = LotusThemeManager()
        self._ui_manager = LotusUIManager(self)
        self._tab_manager = LotusTabManager(self._ui_manager, self._files_manager)
        self._action_controller = LotusActionManager(self._tab_manager, self._ui_manager)
        self._setup_ui()
        self._setup_tabs()
        self._connect_signals()

    def _setup_ui(self):
        self._ui_manager.setup_main_window(
            self.__class__.__name__,
            LotusConfig.get_icon("LOTUS"),
            (100, 100, 1400, 800)
        )
        self._ui_manager.create_main_layout()

    def _setup_tabs(self):
        self._tab_manager.initialize_tabs()

    def _connect_signals(self):
        self._ui_manager.connect_signals()
        # Application-level signals
        self._ui_manager.exitRequested.connect(self.close)
        self._ui_manager.toggleThemeRequested.connect(self._theme_manager.toggle_theme)

    def closeEvent(self, event):
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
                event.ignore()
                return
        event.accept()