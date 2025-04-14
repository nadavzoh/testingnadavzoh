from PyQt5.QtCore import QObject, pyqtSignal


class AbstractDialogController(QObject):
    """
    Abstract base class for all dialog controllers in the Lotus application.
    Each dialog controller should implement this interface.
    """
    dialog_accepted = pyqtSignal(str)
    dialog_cancelled = pyqtSignal()

    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view
        self.edit_mode = False
        self._connect_signals()

    def _connect_signals(self):
        """Connect signals from the view to slots in this controller."""
        raise NotImplementedError("Subclasses must implement _connect_signals")

    def toggle_tab_editable(self, editable):
        """Enable or disable editing of the current tab."""
        raise NotImplementedError("Subclasses must implement toggle_tab_editable")

    def fill_dialog_with_line(self, line):
        """Fill the dialog with data parsed from a line."""
        raise NotImplementedError("Subclasses must implement fill_dialog_with_line")

    def set_edit_mode(self, is_edit):
        """Set whether the dialog is in edit mode."""
        raise NotImplementedError("Subclasses must implement set_edit_mode")