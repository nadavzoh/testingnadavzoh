class MutexDialogController:
    """Controller class to handle user interactions."""

    def __init__(self, model, view):
        """Initialize with model and view instances."""
        self.model = model
        self.view = view.main_tab

        # Connect button signals to slots
        self.view.move_right_button.clicked.connect(self.move_item_to_right)
        self.view.move_left_button.clicked.connect(self.move_item_to_left)

        # Initial update of view
        self.update_view()

    def move_item_to_right(self):
        """Handle moving selected item from left to right."""
        # Get the selected index from the left list view
        indexes = self.view.left_list_view.selectedIndexes()
        if indexes:
            # Only use the first selected item
            index = indexes[0].row()
            if self.model.move_to_right(index):
                self.update_view()

    def move_item_to_left(self):
        """Handle moving selected item from right to left."""
        # Get the selected index from the right list view
        indexes = self.view.right_list_view.selectedIndexes()
        if indexes:
            # Only use the first selected item
            index = indexes[0].row()
            if self.model.move_to_left(index):
                self.update_view()

    def update_view(self):
        """Update the view with current model data."""
        self.view.update_lists(
            self.model.get_left_items(),
            self.model.get_right_items()
        )