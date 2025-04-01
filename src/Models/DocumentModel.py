# DocumentModel.py
import re

class DocumentModel:
    def __init__(self, input_file, data_file):
        self.dcfg_file = input_file
        self.dcfg_file_content = []  # Current working copy
        self.original_content = []  # Backup of file contents
        if input_file:
            self.load_dcfg_file(input_file)

        """ might remove data file because everything is being done through FlyNetlist, for AF atleast..
        check for mutex"""
        self.data_file_content = []
        if data_file:
            self.load_data_file(data_file)

        self.current_selected_index = -1  # Track selected line
        # Add history for undo
        self.action_history = []  # List of (action_type, data) tuples
        self.redo_history = []  # List of (action_type, data) tuples
        self.max_history = 50  # Maximum actions to track

    def load_dcfg_file(self, file_path):
        """Load regex patterns from a file."""
        try:
            with open(file_path, 'r') as file:
                self.dcfg_file_content = [line.strip() for line in file.readlines()]
            self.original_content = self.dcfg_file_content.copy()
            return True
        except Exception as e:
            print(f"Error loading regex file: {e}")
            return False

    def load_data_file(self, file_path):
        """Load data lines to be searched with regex patterns."""
        try:
            with open(file_path, 'r') as file:
                self.data_file_content = [line.strip() for line in file.readlines()]
            return True
        except Exception as e:
            print(f"Error loading data file: {e}")
            return False

    def insert_line(self, line, index):
        """Insert a new line at the specified index or at the end of the file."""
        if index == -1:
            index = len(self.dcfg_file_content)
        # else:
        self.dcfg_file_content.insert(index, line)  # Insert after current line
        # Record action for undo
        self._record_action('insert', {'position': index, 'line': line})
        return True


    def delete_line(self, index=None):
        """Delete the line at specified index or selected position."""
        if index is None:
            index = self.current_selected_index

        if 0 <= index < len(self.dcfg_file_content):
            deleted_line = self.dcfg_file_content[index]
            self._record_action('delete', {'position': index, 'line': deleted_line})
            del self.dcfg_file_content[index]
            if self.current_selected_index >= len(self.dcfg_file_content):
                self.current_selected_index = len(self.dcfg_file_content) - 1
            return True
        return False

    def edit_current_line(self, new_line):
        """Edit the currently selected line."""
        index = self.current_selected_index
        if 0 <= index < len(self.dcfg_file_content):
            self._record_action('edit', {'position': index, 'new_line': new_line, 'old_line': self.dcfg_file_content[index]})
            self.dcfg_file_content[index] = new_line
            return True
        return False

    def _record_action(self, action_type, data):
        """Record an action for undo functionality."""
        self.action_history.append((action_type, data))
        # Limit history size
        if len(self.action_history) > self.max_history:
            self.action_history.pop(0)

    def undo_last_action(self):
        """Undo the last action if available."""
        if not self.action_history:
            return False
        # Get the last action
        action_type, data = self.action_history.pop()
        self.redo_history.append((action_type, data))

        if action_type == 'insert':
            # For insert, we need to delete the line
            position = data['position']
            if 0 <= position < len(self.dcfg_file_content):
                del self.dcfg_file_content[position]
                # Update current selected index
                self.current_selected_index = max(0, position - 1) if self.dcfg_file_content else -1
                return True

        elif action_type == 'delete':
            # For delete, we need to insert the line back
            position = data['position']
            line = data['line']

            # Make sure position is valid
            if position <= len(self.dcfg_file_content):
                self.dcfg_file_content.insert(position, line)
                # Set the selected index to the restored line
                self.current_selected_index = position
                return True

        elif action_type == 'comment':
            # For comment, we need to uncomment the line
            position = data['position']
            if 0 <= position < len(self.dcfg_file_content):
                line = self.dcfg_file_content[position]
                if line.startswith("#"):
                    self.dcfg_file_content[position] = line[2:]
                return True

        elif action_type == 'edit':
            # For edit, we need to restore the old line
            position = data['position']
            old_line = data['old_line']
            if 0 <= position < len(self.dcfg_file_content):
                self.dcfg_file_content[position] = old_line
                return True

        return False

    def redo_action(self):
        """Redo the last action if available."""
        if not self.redo_history:
            return False
        # Get the last action
        action_type, data = self.redo_history.pop()
        self.action_history.append((action_type, data))

        if action_type == 'insert':
            # For insert, we need to insert the line back
            position = data['position']
            line = data['line']

            # Make sure position is valid
            if position <= len(self.dcfg_file_content):
                self.dcfg_file_content.insert(position, line)
                # Set the selected index to the restored line
                self.current_selected_index = position
                return True

        elif action_type == 'delete':
            # For delete, we need to delete the line
            position = data['position']
            if 0 <= position < len(self.dcfg_file_content):
                del self.dcfg_file_content[position]
                # Update current selected index
                self.current_selected_index = max(0, position - 1) if self.dcfg_file_content else -1
                return True

        elif action_type == 'comment':
            # For comment, we need to comment the line
            position = data['position']
            if 0 <= position < len(self.dcfg_file_content):
                line = self.dcfg_file_content[position]
                if not line.startswith("#"):
                    self.dcfg_file_content[position] = f"# {line}"
                return True

        elif action_type == 'edit':
            # For edit, we need to update the line
            position = data['position']
            new_line = data['new_line']
            if 0 <= position < len(self.dcfg_file_content):
                self.dcfg_file_content[position] = new_line
                return True
        return False

    def save_to_file(self):
        """Save updated file."""
        if not self.dcfg_file:
            return False

        try:
            with open(self.dcfg_file, 'w') as file:
                file.write("\n".join(self.dcfg_file_content))
            self.original_content = self.dcfg_file_content.copy()
            return True
        except Exception as e:
            print(f"Error saving regex file: {e}")
            return False

    def has_unsaved_changes(self):
        """Check if there are unsaved changes."""
        return self.dcfg_file_content != self.original_content

    def set_selected_index(self, index):
        """Set the currently selected line index."""
        if 0 <= index < len(self.dcfg_file_content):
            self.current_selected_index = index
            return True
        return False