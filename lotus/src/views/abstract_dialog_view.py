from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QDialogButtonBox, QHBoxLayout, QLabel, QTextEdit, \
    QMessageBox


class AbstractDialogView(QWidget):
    """
    Abstract base class for dialog views in the Lotus application.

    This class provides a common structure and behavior for all dialog views,
    including standard tabs, buttons, and error handling. It creates a consistent
    UI experience across different dialog types.

    Dialog views are part of the Model-View-Controller pattern, representing the
    user interface component that displays data and captures user input.

    Attributes:
        tabs (QTabWidget): Tab widget containing dialog pages
        button_box (QDialogButtonBox): Standard button box with Save/Reset/Cancel
        save_line_button (QPushButton): Reference to the Save button
        reset_button (QPushButton): Reference to the Reset button
        cancel_button (QPushButton): Reference to the Cancel button
        comment_edit (QTextEdit): Text area for entering comments
    """

    def __init__(self, parent=None):
        """
        Initialize the dialog view.

        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setGeometry(1100, 200, 800, 800)
        self._setup_ui()

    def _setup_ui(self):
        """
        Set up the user interface components.

        Creates the basic UI structure including main layout, tab widget,
        and standard button box used by all dialog views.
        """
        # Common UI setup - create the main layout and tabs
        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Add specific tabs - this will be implemented by child classes
        self._create_tabs()

        # Common standard button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Reset | QDialogButtonBox.Cancel,
                                           Qt.Horizontal)
        self.save_line_button = self.button_box.button(QDialogButtonBox.Save)
        self.save_line_button.setShortcut("Ctrl+Shift+E")
        self.reset_button = self.button_box.button(QDialogButtonBox.Reset)
        self.reset_button.setShortcut("Ctrl+R")
        self.cancel_button = self.button_box.button(QDialogButtonBox.Cancel)
        self.cancel_button.setShortcut("Esc")

        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def _create_tabs(self):
        """
        Create specific tabs for the dialog.

        This method should be implemented by child classes to create
        dialog-specific tabs with appropriate input fields.
        """
        raise NotImplementedError("Subclasses must implement _create_tabs")

    def _create_comment_tab(self):
        """
        Create the comment tab with a text edit field.

        This is a common tab used across different dialog views for
        adding comments to configuration entries.

        Returns:
            QWidget: The configured comment tab
        """
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Comment:"))

        comment_line = QWidget()
        comment_line_layout = QHBoxLayout()
        comment_line_layout.setContentsMargins(0, 0, 0, 0)
        comment_line_layout.addWidget(QLabel("#"))

        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Write comment here")
        comment_line_layout.addWidget(self.comment_edit)

        comment_line.setLayout(comment_line_layout)
        layout.addWidget(comment_line)

        tab.setLayout(layout)
        return tab

    def show_error(self, title, message):
        """
        Show an error message box.

        Displays a modal error dialog with the specified title and message.

        Args:
            title (str): Title for the error dialog
            message (str): Detailed error message to display
        """
        QMessageBox.critical(self, title, message)

    def clear_comment_tab(self):
        """
        Clear the comment tab.

        Resets the comment text area to empty.
        """
        if hasattr(self, 'comment_edit'):
            self.comment_edit.clear()

    def clear_form(self):
        """
        Clear all input fields in the dialog.

        This method should reset all form fields to their default values.
        """
        raise NotImplementedError("Subclasses must implement clear_form")

    def fill_from_data(self, data):
        """
        Fill the form with the provided data.

        This method should populate all form fields based on the provided data.

        Args:
            data (dict): The data to populate the form with
        """
        raise NotImplementedError("Subclasses must implement fill_from_data")

    def set_editable(self, editable):
        """
        Enable or disable editing of form fields.

        Controls whether users can interact with and modify form fields.

        Args:
            editable (bool): Whether fields should be editable
        """
        # Enable or disable comment tab
        if hasattr(self, 'comment_edit') and self.tabs.currentIndex() == 1:
            self.comment_edit.setEnabled(editable)

        # Enable or disable common buttons
        self.save_line_button.setEnabled(editable)
        self.cancel_button.setEnabled(editable)

        # This method can and should be overridden by subclasses to enable/disable their own fields
        # But this is a default and shared implementation, subclasses may use super() to call this method aswell