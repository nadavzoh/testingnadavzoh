from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListView, QPushButton)

class MutexDialogView(QWidget):
    """View class to display the two lists and buttons."""

    def __init__(self):
        """Initialize the view with two list views and buttons."""
        super().__init__()

        # Create layouts
        main_layout = QHBoxLayout()
        button_layout = QVBoxLayout()

        # Create list views
        self.left_list_view = QListView()
        self.right_list_view = QListView()

        # Create the models for the list views
        self.left_model = QStringListModel()
        self.right_model = QStringListModel()

        # Connect models to views
        self.left_list_view.setModel(self.left_model)
        self.right_list_view.setModel(self.right_model)

        # Create buttons
        self.move_right_button = QPushButton("→")
        self.move_left_button = QPushButton("←")

        # Add buttons to layout
        button_layout.addStretch()
        button_layout.addWidget(self.move_right_button)
        button_layout.addWidget(self.move_left_button)
        button_layout.addStretch()

        # Arrange components in the main layout
        main_layout.addWidget(self.left_list_view)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.right_list_view)

        # Set the main layout
        self.setLayout(main_layout)

        # Set window properties
        self.resize(600, 400)

    def update_lists(self, left_items, right_items):
        """Update both list views with new data."""
        self.left_model.setStringList(left_items)
        self.right_model.setStringList(right_items)