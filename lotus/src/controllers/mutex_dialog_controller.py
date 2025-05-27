from PyQt5.QtCore import pyqtSignal
from controllers.af_dialog_controller import AbstractDialogController

"""
PLACEHOLDER, NOT ACTUAL IMPLEMENTATION
"""
class MutexDialogController(AbstractDialogController):
    """Controller class for mutex dialog interactions."""

    def __init__(self, model, view):
        """Initialize with model and view instances."""
        super().__init__(model, view)
        # Initial update of view
        self.update_view()

    def _connect_signals(self):
        """Connect signals from the view to slots in this controller."""
        # Connect main tab button signals
        self.view.itemMovedToRight.connect(self.move_item_to_right)
        self.view.itemMovedToLeft.connect(self.move_item_to_left)

        # Connect common buttons
        self.view.reset_button.clicked.connect(self._on_clear_dialog_requested)
        self.view.cancel_button.clicked.connect(self._on_cancel_dialog)
        self.view.save_line_button.clicked.connect(self._on_save_line_requested)

    def toggle_tab_editable(self, editable):
        """Enable or disable editing of the current tab."""
        self.view.set_editable(editable)

    def move_item_to_right(self, index):
        """Handle moving selected item from left to right."""
        if self.model.move_to_right(index):
            self.update_view()

    def move_item_to_left(self, index):
        """Handle moving selected item from right to left."""
        if self.model.move_to_left(index):
            self.update_view()

    def update_view(self):
        """Update the view with current model data."""
        self.view.update_lists(
            self.model.get_left_items(),
            self.model.get_right_items()
        )

    def fill_dialog_with_line(self, line):
        """Fill the dialog with data parsed from a line."""
        if line.startswith('#'):
            # It's a comment line - directly pass to view
            self.view.fill_from_data(line)
        else:
            # Handle mutex config line parsing
            # This would need to be implemented based on mutex file format
            # For now, we'll just show the comment tab
            self.view.tabs.setCurrentIndex(0)  # Switch to Mutex tab
            # Parse and update the mutex lists - to be implemented

    def _on_cancel_dialog(self):
        """Handle dialog cancellation."""
        self.dialog_cancelled.emit()
        self.toggle_tab_editable(False)

    def _on_save_line_requested(self):
        """Handle save button click."""
        if self.view.tabs.currentIndex() == 0:  # Mutex tab
            # Generate mutex config line based on selected items
            # For now, just emit a placeholder
            left_items = self.model.get_left_items()
            right_items = self.model.get_right_items()

            if right_items:
                # Example
                mutex_line = "MUTEX " + " ".join(right_items)
                self.dialog_accepted.emit(mutex_line)
            else:
                self.view.show_error("Validation Error", "You must select at least one item for the mutex rule")
                return

        elif self.view.tabs.currentIndex() == 1:  # Comment tab
            self.dialog_accepted.emit(f"# {self.view.comment_edit.toPlainText()}")

        self.dialog_cancelled.emit()
        self.toggle_tab_editable(False)

    def _on_clear_dialog_requested(self):
        """Handle reset button click."""
        self.view.clear_form()

    def set_edit_mode(self, is_edit):
        """Set whether the dialog is in edit mode."""
        self.edit_mode = is_edit
        self.toggle_tab_editable(is_edit)