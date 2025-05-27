from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from managers.lotus_theme_manager import LotusThemeManager

class LotusActionManager(QObject):
    """
    Central controller that coordinates actions between UI elements and tab controllers.

    This class acts as a mediator between the UI components and the underlying
    controllers, decoupling the main application from direct handling of button actions.
    It routes UI events to appropriate controllers and handles common
    feedback mechanisms like notifications.

    Attributes:
        tab_manager: Manager providing access to tab controllers
        ui_manager: Manager providing access to UI components and signals
        showInfoMessage (pyqtSignal): Signal emitted to show information messages
        showWarningMessage (pyqtSignal): Signal emitted to show warning messages
    """

    # Signals for notifications that will be shown to the user
    showInfoMessage = pyqtSignal(str, str)  # title, message
    showWarningMessage = pyqtSignal(str, str)  # title, message

    def __init__(self, tab_manager, ui_manager):
        """
        Initialize with tab manager and UI manager.

        Args:
            tab_manager: The tab manager that provides controllers for tabs
            ui_manager: The UI manager that provides UI elements and signals
        """
        super().__init__()
        self.tab_manager = tab_manager
        self.ui_manager = ui_manager
        self._theme_manager = LotusThemeManager()
        self._connect_signals()

    def _connect_signals(self):
        """
        Connect UI signals to handler methods.

        Wires up all signals from UI components to their corresponding
        handler methods in this class, and connects notification signals
        back to the UI manager for display.
        """
        # Connect signals from UI manager
        self.ui_manager.insertRequested.connect(self._on_insert_requested)
        self.ui_manager.editRequested.connect(self._on_edit_requested)
        self.ui_manager.deleteRequested.connect(self._on_delete_requested)
        self.ui_manager.undoRequested.connect(self._on_undo_requested)
        self.ui_manager.redoRequested.connect(self._on_redo_requested)
        self.ui_manager.saveRequested.connect(self._on_save_requested)
        self.ui_manager.saveAsRequested.connect(self._on_save_file_as)
        self.ui_manager.saveAllRequested.connect(self._on_save_all_requested)

        self.ui_manager.increaseFontSizeRequested.connect(self._theme_manager.increase_font_size)
        self.ui_manager.decreaseFontSizeRequested.connect(self._theme_manager.decrease_font_size)
        self.ui_manager.resetFontSizeRequested.connect(self._theme_manager.reset_font_size)
        self.ui_manager.toggleThemeRequested.connect(self._theme_manager.toggle_theme)

        # Connect notification signals back to UI
        self.showInfoMessage.connect(self.ui_manager.show_info_message)
        self.showWarningMessage.connect(self.ui_manager.show_warning_message)

    @pyqtSlot()
    def _on_insert_requested(self):
        """
        Handle insert action.

        Delegates to the active controller to insert a new line at the
        current position and shows a warning if insertion fails.
        """
        controller = self.tab_manager.get_active_controller()
        if controller:
            success = controller.insert_line("")
            if not success:
                self.showWarningMessage.emit("Insert Line", "No line selected to insert after.")

    @pyqtSlot()
    def _on_edit_requested(self):
        """
        Handle edit action.

        Disables UI buttons and puts the active controller into edit mode.
        This typically opens a dialog for editing the selected line.
        """
        self.ui_manager.disable_buttons()
        controller = self.tab_manager.get_active_controller()
        if controller:
            controller.enter_edit_mode()

    @pyqtSlot()
    def _on_delete_requested(self):
        """
        Handle delete action.

        Delegates to the active controller to delete the currently selected line.
        """
        controller = self.tab_manager.get_active_controller()
        if controller:
            controller.delete_line()

    @pyqtSlot()
    def _on_undo_requested(self):
        """
        Handle undo action.

        Delegates to the active controller to undo the last action and
        shows an information message if there's nothing to undo.
        """
        controller = self.tab_manager.get_active_controller()
        if controller:
            success = controller.undo_action()
            if not success:
                self.showInfoMessage.emit("Undo", "Nothing to undo.")

    @pyqtSlot()
    def _on_redo_requested(self):
        """
        Handle redo action.

        Delegates to the active controller to redo the previously undone action
        and shows an information message if there's nothing to redo.
        """
        controller = self.tab_manager.get_active_controller()
        if controller:
            success = controller.redo_action()
            if not success:
                self.showInfoMessage.emit("Redo", "Nothing to redo.")

    @pyqtSlot()
    def _on_save_requested(self):
        """
        Handle save action.

        Delegates to the active controller to save changes and shows
        an appropriate message based on the result.
        """
        controller = self.tab_manager.get_active_controller()
        if controller:
            success = controller.save_changes()
            if success:
                self.showInfoMessage.emit("Save", "Changes saved successfully.")
            else:
                self.showWarningMessage.emit("Save", "Failed to save changes.")

    @pyqtSlot()
    def _on_save_file_as(self):
        """
        Save the current file to a new location.

        Returns:
            bool: True if saved successfully, False otherwise
        """
        controller = self.tab_manager.get_active_controller()
        if not controller:
            return False
        document = controller.model
        old_filepath = document.get_dcfg_file()

        new_filepath = self.ui_manager.show_save_as_dialog()
        if not new_filepath:
            return False  # user canceled

        document.set_dcfg_file(new_filepath)
        success = document.save_to_file()

        if success:
            self.ui_manager.update_header_filepath(new_filepath)
            self.ui_manager.show_info_message("File Saved", f"File saved as:\n{new_filepath}")
        else:
            document.set_dcfg_file(old_filepath)
            self.ui_manager.show_warning_message("Save Failed", f"Could not save file to:\n{new_filepath}")

        return success

    @pyqtSlot()
    def _on_save_all_requested(self):
        """
        Handle save all action.

        Iterates through all controllers and saves their changes.
        Shows a warning and stops if any save operation fails.
        """
        all_controllers = self.tab_manager.get_controllers()
        for controller in all_controllers:
            if controller.has_unsaved_changes():
                success = controller.save_changes()
                if not success:
                    self.showWarningMessage.emit("Save All", "Failed to save all changes.")
                    return
        self.showInfoMessage.emit("Save All", "All changes saved successfully.")

    def check_for_unsaved_changes(self):
        """
        Check if any tab has unsaved changes.

        Returns:
            bool: True if any tab has unsaved changes, False otherwise.
        """
        for controller in self.tab_manager.get_controllers():
            if controller.has_unsaved_changes():
                return True
        return False