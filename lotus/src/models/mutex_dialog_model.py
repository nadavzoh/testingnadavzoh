"""
PLACEHOLDER
"""

class MutexDialogModel:
    """Model class to manage the data between the two lists."""

    def __init__(self, initial_items=None):
        """Initialize with optional list of items."""
        if initial_items is None:
            initial_items = []

        # Store all items in two separate lists
        self.left_items = initial_items.copy()
        self.right_items = []

    def move_to_right(self, index):
        """Move an item from the left list to the right list."""
        if 0 <= index < len(self.left_items):
            item = self.left_items.pop(index)
            self.right_items.append(item)
            return True
        return False

    def move_to_left(self, index):
        """Move an item from the right list to the left list."""
        if 0 <= index < len(self.right_items):
            item = self.right_items.pop(index)
            self.left_items.append(item)
            return True
        return False

    def get_left_items(self):
        """Return the items in the left list."""
        return self.left_items

    def get_right_items(self):
        """Return the items in the right list."""
        return self.right_items