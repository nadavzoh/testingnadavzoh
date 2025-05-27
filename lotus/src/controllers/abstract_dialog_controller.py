from PyQt5.QtCore import QObject, pyqtSignal


class AbstractDialogController(QObject):
    """
    Abstract base class for all dialog controllers in the Lotus application.

    This class defines the interface and common functionality that all dialog
    controllers must implement. Dialog controllers manage the interaction between
    dialog views and models, handling UI events and updating the model.

    Dialog controllers are part of the Model-View-Controller pattern, serving as
    the intermediary between the UI (view) and data (model) components.

    Signals:
        dialog_accepted (str): Emitted when the dialog is accepted, with resulting data\n
        dialog_cancelled: Emitted when the dialog is cancelled

    Attributes:
        model: The data model associated with this dialog
        view: The view (UI) associated with this dialog
        edit_mode (bool): Whether the dialog is in edit mode
    """
    dialog_accepted = pyqtSignal(str)
    dialog_cancelled = pyqtSignal()

    def __init__(self, model, view):
        """
        Initialize the dialog controller.

        Args:
            model: The data model for this dialog
            view: The view (UI) for this dialog
        """
        super().__init__()
        self.model = model
        self.view = view
        self.edit_mode = False
        self._connect_signals()

    def _connect_signals(self):
        """
        Connect signals from the view to slots in this controller.

        This method should establish all necessary connections between UI events
        (like button clicks) and their corresponding handler methods in the controller.
        """
        raise NotImplementedError("Subclasses must implement _connect_signals")

    def toggle_tab_editable(self, editable):
        """
        Enable or disable editing of the form fields.

        Args:
            editable (bool): Whether fields should be editable
        """
        raise NotImplementedError("Subclasses must implement toggle_tab_editable")

    def fill_dialog_with_line(self, line):
        """
        Fill the dialog with data parsed from a configuration line.

        This method should populate the dialog fields with values from the provided line.

        Args:
            line (str): The configuration line to parse and display
        """
        raise NotImplementedError("Subclasses must implement fill_dialog_with_line")

    def set_edit_mode(self, is_edit):
        """
        Set whether the dialog is in edit mode.

        Args:
            is_edit (bool): Whether the dialog should be in edit mode
        """
        raise NotImplementedError("Subclasses must implement set_edit_mode")