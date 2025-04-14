class DocumentController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.dialog_controller = None

        self.view.update_content(self.model.dcfg_file_content)
        self.view.lineSelected.connect(self.on_line_selected)
        self.view.lineDoubleClicked.connect(self.on_line_double_clicked)
        self.view.cancelSelection.connect(self._on_line_selection_cancelled)

    def set_dialog_controller(self, dialog_controller):
        self.dialog_controller = dialog_controller
        self.dialog_controller.dialog_accepted.connect(lambda line: self.edit_line(line))
        self.dialog_controller.dialog_accepted.connect(lambda: self.view.setEnabled(True))
        self.dialog_controller.dialog_cancelled.connect(self._on_cancel_dialog)
        self.dialog_controller.dialog_cancelled.connect(lambda: self.view.setEnabled(True))


    def on_line_selected(self, index):
        """Handle pattern selection from the view."""
        self.model.set_selected_index(index)

    def on_line_double_clicked(self, index):
        """Handle pattern selection from the view."""
        if self.dialog_controller and index >= 0:
            line = self.model.dcfg_file_content[index]
            self.dialog_controller.fill_dialog_with_line(line)

    def _on_line_selection_cancelled(self):
        self.dialog_controller._on_clear_dialog_requested()

    def insert_line(self, line):
        """Insert a new line at the currently selected line."""
        index = self.view.get_selected_index()
        success = self.model.insert_line(line, index)
        if success:
            self.view.update_content(self.model.dcfg_file_content)
            if index == -1:
                index = len(self.model.dcfg_file_content) - 1
            self.view.select_line(index)
            self.on_line_selected(index)
        return success

    def edit_line(self, line):
        """Edit the currently selected line."""
        success = self.model.edit_current_line(line)
        if success:
            self.view.update_content(self.model.dcfg_file_content)
            self.view.select_line(self.model.current_selected_index)
            self.on_line_selected(self.model.current_selected_index)
            self.dialog_controller.set_edit_mode(False)
        return success

    def enter_edit_mode(self):
        """Sends a signal to the dialog controller to enable the save button."""
        self.dialog_controller.set_edit_mode(True)
        self.view.setEnabled(False)

    def _on_cancel_dialog(self):
        """Cancel the dialog and re-enable the view."""
        self.dialog_controller.set_edit_mode(False)
        self.view.setEnabled(True)

    def delete_line(self):
        """Delete the currently selected line."""
        index = self.view.get_selected_index()
        success = self.model.delete_line(index)
        if success:
            self.view.update_content(self.model.dcfg_file_content)
            # Select the line at the same position (or last line if deleted last)
            new_index = min(index, len(self.model.dcfg_file_content) - 1)
            if new_index >= 0:
                self.view.select_line(new_index)
                self.on_line_selected(new_index)
        return success

    def undo_action(self):
        """Undo the last action."""
        success = self.model.undo_last_action()
        if success:
            self.view.update_content(self.model.dcfg_file_content)
            # Select the appropriate line after undo
            if self.model.current_selected_index >= 0:
                self.view.select_line(self.model.current_selected_index)
                self.on_line_selected(self.model.current_selected_index)
        return success

    def redo_action(self):
        """Redo the last undone action."""
        success = self.model.redo_action()
        if success:
            self.view.update_content(self.model.dcfg_file_content)
            # Select the appropriate line after redo
            if self.model.current_selected_index >= 0:
                self.view.select_line(self.model.current_selected_index)
                self.on_line_selected(self.model.current_selected_index)
        return success

    def save_changes(self):
        """Save changes to file."""
        success = self.model.save_to_file()
        return success

    def has_unsaved_changes(self):
        """Check if there are unsaved changes."""
        return self.model.has_unsaved_changes()