from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class LotusActionManager(QObject):
    """
    Central controller that coordinates actions between UI elements and tab controllers.
    This decouples the Lotus main class from direct handling of button actions.
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
        self._connect_signals()

    def _connect_signals(self):
        """Connect UI signals to handler methods."""
        # Connect signals from UI manager
        self.ui_manager.insertRequested.connect(self._on_insert_requested)
        self.ui_manager.editRequested.connect(self._on_edit_requested)
        self.ui_manager.deleteRequested.connect(self._on_delete_requested)
        self.ui_manager.undoRequested.connect(self._on_undo_requested)
        self.ui_manager.redoRequested.connect(self._on_redo_requested)
        self.ui_manager.saveRequested.connect(self._on_save_requested)
        self.ui_manager.saveAllRequested.connect(self._on_save_all_requested)

        # Connect our notification signals back to UI
        self.showInfoMessage.connect(self.ui_manager.show_info_message)
        self.showWarningMessage.connect(self.ui_manager.show_warning_message)

    @pyqtSlot()
    def _on_insert_requested(self):
        """Handle insert action."""
        controller = self.tab_manager.get_active_controller()
        if controller:
            success = controller.insert_line("")
            if not success:
                self.showWarningMessage.emit("Insert Line", "No line selected to insert after.")

    @pyqtSlot()
    def _on_edit_requested(self):
        """Handle edit action."""
        self.ui_manager.disable_buttons()
        controller = self.tab_manager.get_active_controller()
        if controller:
            controller.enter_edit_mode()

    @pyqtSlot()
    def _on_delete_requested(self):
        """Handle delete action."""
        controller = self.tab_manager.get_active_controller()
        if controller:
            controller.delete_line()

    @pyqtSlot()
    def _on_undo_requested(self):
        """Handle undo action."""
        controller = self.tab_manager.get_active_controller()
        if controller:
            success = controller.undo_action()
            if not success:
                self.showInfoMessage.emit("Undo", "Nothing to undo.")

    @pyqtSlot()
    def _on_redo_requested(self):
        """Handle redo action."""
        controller = self.tab_manager.get_active_controller()
        if controller:
            success = controller.redo_action()
            if not success:
                self.showInfoMessage.emit("Redo", "Nothing to redo.")

    @pyqtSlot()
    def _on_save_requested(self):
        """Handle save action."""
        controller = self.tab_manager.get_active_controller()
        if controller:
            success = controller.save_changes()
            if success:
                self.showInfoMessage.emit("Save", "Changes saved successfully.")
            else:
                self.showWarningMessage.emit("Save", "Failed to save changes.")

    @pyqtSlot()
    def _on_save_all_requested(self):
        """Handle save all action."""
        all_controllers = self.tab_manager.get_controllers()
        for controller in all_controllers:
            if controller.has_unsaved_changes():
                success = controller.save_changes()
                if not success:
                    self.showWarningMessage.emit("Save All", "Failed to save all changes.")
                    return
        self.showInfoMessage.emit("Save All", "All changes saved successfully.")

    def check_for_unsaved_changes(self):
        """Check if any tab has unsaved changes."""
        for controller in self.tab_manager.get_controllers():
            if controller.has_unsaved_changes():
                return True
        return False