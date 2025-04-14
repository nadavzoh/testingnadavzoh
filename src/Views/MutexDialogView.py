from PyQt5.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QListView,
    QPushButton, QWidget
)

from src.Views.AbstractDialogView import AbstractDialogView


class MutexDialogView(AbstractDialogView):
    """
    Dialog view for Mutex configuration.
    Directly implements all UI components without nested views.
    """
    itemMovedToRight = pyqtSignal(int)  # Index of item moved to right
    itemMovedToLeft = pyqtSignal(int)  # Index of item moved to left

    def __init__(self, parent=None):
        self.left_model = QStringListModel()
        self.right_model = QStringListModel()
        super().__init__(parent)

    def _create_specific_tabs(self):
        """Create the specific tabs for this dialog view."""
        # Create Mutex tab
        self.mutex_tab = self._create_mutex_tab()
        self.tabs.addTab(self.mutex_tab, "Mutex")

        # Create Comment tab using parent method
        self.comment_tab = self._create_comment_tab()
        self.tabs.addTab(self.comment_tab, "Comment")

    def _create_mutex_tab(self):
        """Create the mutex tab with lists and movement buttons."""
        tab = QWidget()
        main_layout = QHBoxLayout()

        # Create list views
        self.left_list_view = QListView()
        self.right_list_view = QListView()

        # Connect models to views
        self.left_list_view.setModel(self.left_model)
        self.right_list_view.setModel(self.right_model)

        # Create buttons
        button_layout = QVBoxLayout()
        self.move_right_button = QPushButton("→")
        self.move_left_button = QPushButton("←")

        # Connect button signals
        self.move_right_button.clicked.connect(self._on_move_right_clicked)
        self.move_left_button.clicked.connect(self._on_move_left_clicked)

        # Add buttons to layout
        button_layout.addStretch()
        button_layout.addWidget(self.move_right_button)
        button_layout.addWidget(self.move_left_button)
        button_layout.addStretch()

        # Arrange components in the main layout
        main_layout.addWidget(self.left_list_view)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.right_list_view)

        tab.setLayout(main_layout)
        return tab

    def _on_move_right_clicked(self):
        """Handle move right button click."""
        indexes = self.left_list_view.selectedIndexes()
        if indexes:
            self.itemMovedToRight.emit(indexes[0].row())

    def _on_move_left_clicked(self):
        """Handle move left button click."""
        indexes = self.right_list_view.selectedIndexes()
        if indexes:
            self.itemMovedToLeft.emit(indexes[0].row())

    def update_lists(self, left_items, right_items):
        """Update both list views with new data."""
        self.left_model.setStringList(left_items)
        self.right_model.setStringList(right_items)

    def clear_form(self):
        """Clear all input fields in the current tab."""
        # For mutex tab, clearing would be implemented when needed
        # We could reset the lists if needed

        # Clear comment tab
        if self.tabs.currentIndex() == 1:
            self.clear_comment_tab()

    def fill_from_data(self, data):
        """Fill the form with the provided data."""
        if isinstance(data, dict):
            # Fill mutex data when implemented
            self.tabs.setCurrentIndex(0)
        elif isinstance(data, str) and data.startswith("#"):
            # Switch to Comment tab for comments
            self.tabs.setCurrentIndex(1)
            self.comment_edit.setText(data.strip("#").strip())

    def set_editable(self, editable):
        """Enable or disable editing of form fields."""
        # Call parent implementation for common components
        super().set_editable(editable)

        # Mutex-specific components
        if self.tabs.currentIndex() == 0:  # Mutex tab
            self.move_right_button.setEnabled(editable)
            self.move_left_button.setEnabled(editable)