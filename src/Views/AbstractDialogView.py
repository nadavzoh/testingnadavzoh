from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QDialogButtonBox, QHBoxLayout, QLabel, QTextEdit, \
    QMessageBox
# Remove ABC import and use NotImplementedError instead
from abc import abstractmethod

class AbstractDialogView(QWidget):
    """
    Abstract base class for dialog views in the Lotus application.
    Each dialog view should implement this interface.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(1100, 200, 800, 800)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface components."""
        # Common UI setup - create the main layout and tabs
        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Add specific tabs - this will be implemented by child classes
        self._create_specific_tabs()

        # Add the standard button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Reset | QDialogButtonBox.Cancel,
                                           Qt.Horizontal)
        self.save_line_button = self.button_box.button(QDialogButtonBox.Save)
        self.reset_button = self.button_box.button(QDialogButtonBox.Reset)
        self.cancel_button = self.button_box.button(QDialogButtonBox.Cancel)

        # Add tabs and buttons to layout
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.button_box)

        # Set the layout
        self.setLayout(self.layout)

    def _create_specific_tabs(self):
        """Create specific tabs for the dialog. To be implemented by child classes."""
        # Using NotImplementedError instead of @abstractmethod decorator
        raise NotImplementedError("Subclasses must implement _create_specific_tabs")

    def _create_comment_tab(self):
        """Create the comment tab with a text edit field - common to all dialog views."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Comment label
        layout.addWidget(QLabel("Comment:"))

        # Comment input with prefix
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
        """Show an error message box. Common to all dialog views."""
        QMessageBox.critical(self, title, message)

    def clear_comment_tab(self):
        """Clear the comment tab. Common to all dialog views."""
        if hasattr(self, 'comment_edit'):
            self.comment_edit.clear()

    def clear_form(self):
        """Clear all input fields."""
        # Using NotImplementedError instead of @abstractmethod decorator
        raise NotImplementedError("Subclasses must implement clear_form")

    def fill_from_data(self, data):
        """Fill the form with the provided data."""
        # Using NotImplementedError instead of @abstractmethod decorator
        raise NotImplementedError("Subclasses must implement fill_from_data")

    def set_editable(self, editable):
        """Enable or disable editing of form fields."""
        # Enable or disable comment tab
        if hasattr(self, 'comment_edit') and self.tabs.currentIndex() == 1:
            self.comment_edit.setEnabled(editable)

        # Enable or disable common buttons
        self.save_line_button.setEnabled(editable)
        self.cancel_button.setEnabled(editable)

        # This method can be overridden by subclasses to enable/disable their own fields
        # But we provide a default implementation, so it's not required to override