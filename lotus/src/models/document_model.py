from services.pattern_matcher import PatternMatcher
from models.abstract_line_model import AbstractLineModel
from models.af_line_model import AfLineModel


class DocumentModel:
    """
    Model representing a text document with line-based operations.

    This class manages document state and provides methods for manipulating
    text content on a line-by-line basis. It supports validation of lines,
    saving content to disk, and tracking changes to individual lines.

    Attributes:
        VALID (int): Constant indicating a line is valid
        INVALID (int): Constant indicating a line is invalid
        WARNING (int): Constant indicating a line has a warning
        COMMENT (int): Constant indicating a line is a comment
        dcfg_file (str): Path to the file backing this document
        dcfg_file_content (list): List of strings representing document lines
        original_content (list): Backup of file contents
        line_models (list): List of line model objects
        line_model_class (class): Class to use for line models
        pattern_matcher (PatternMatcher): Pattern matcher for finding matches
        current_selected_index (int): Index of the currently selected line
        action_history (list): List of (action_type, data) tuples for undo
        redo_history (list): List of (action_type, data) tuples for redo
        max_history (int): Maximum actions to track
    """

    # Use constants from the abstract line model
    VALID = AbstractLineModel.VALID
    INVALID = AbstractLineModel.INVALID
    WARNING = AbstractLineModel.WARNING
    COMMENT = AbstractLineModel.COMMENT

    def __init__(self, input_file, data_file=None, line_model_class=None):
        """
        Initialize the document model.

        Args:
            input_file (str): Path to the input file to load.
            data_file (str, optional): Path to the data file. Defaults to None.
            line_model_class (class, optional): Class to use for line models. Defaults to AfLineModel.
        """
        self.dcfg_file = input_file
        self.dcfg_file_content = []  # Current working copy
        self.original_content = []  # Backup of file contents
        self.line_models = []  # List of line model objects

        # Store the line model class to use (default to AfLineModel if none provided, for now)
        # probably better to use a factory method to create line models, later.
        self.line_model_class = line_model_class if line_model_class is not None else AfLineModel

        self.pattern_matcher = PatternMatcher()

        if input_file:
            self.load_dcfg_file(input_file)

        self.current_selected_index = -1  # Track selected line
        # history for undo
        self.action_history = []  # List of (action_type, data) tuples
        self.redo_history = []  # List of (action_type, data) tuples
        self.max_history = 50  # Maximum actions to track

    def load_dcfg_file(self, file_path):
        """
        Loads the dcfg file and creates line models for each line.

        Args:
            file_path (str): Path to the file to load.

        Returns:
            bool: True if the file was loaded successfully, False otherwise.
        """
        try:
            with open(file_path, 'r') as file:
                self.dcfg_file_content = [line.strip() for line in file.readlines()]
            self.original_content = self.dcfg_file_content.copy()

            self._create_line_models()

            return True
        except Exception as e:
            print(f"-I-    No config input file found, defaulting to empty file")
            print(e)
            return False

    def set_dcfg_file(self, filepath):
        """
        Sets the filepath for which the document model points to.
        """
        self.dcfg_file = filepath

    def get_dcfg_file(self):
        """
        Returns the filepath for which the document model points to.
        """
        return self.dcfg_file

    def _create_line_models(self):
        """
        Create line model objects for all lines in the document.
        """
        self.line_models = []  # Reset line models
        for line in self.dcfg_file_content:
            line_model = self._create_line_model(line)
            self.line_models.append(line_model)

    def _create_line_model(self, line):
        """
        Create a new line model instance based on the configured model class.

        Args:
            line (str): The line to create a model for.

        Returns:
            AbstractLineModel: The created line model instance.
        """
        line_model = self.line_model_class(line)

        # If the model supports matches, calculate and set them (this is a tmp fix for AF)
        if hasattr(line_model, 'set_net_matches') and hasattr(line_model, 'set_template_matches'):
            ## TODO: This is a temporary fix for AF, we need to find a better way to do this
            ## DocumentModel should not be responsible for these kind of details...
            if not line.startswith('#') and line.strip():
                net_matches, template_matches = self.find_matches(line)
                line_model.set_net_matches(net_matches)
                line_model.set_template_matches(template_matches)

        return line_model

    def set_line_model_class(self, line_model_class):
        """
        Set the line model class to use for this document.

        Args:
            line_model_class (class): Class that inherits from AbstractLineModel.

        Raises:
            TypeError: If the provided class is not a subclass of AbstractLineModel.
        """
        # Ensure the class is a subclass of AbstractLineModel
        if not issubclass(line_model_class, AbstractLineModel):
            raise TypeError("Line model class must be a subclass of AbstractLineModel")

        self.line_model_class = line_model_class

        if self.dcfg_file_content:
            self._create_line_models()

    def get_validation_status(self, index):
        """
        Get validation status for a line.

        Args:
            index (int): Index of the line to get the validation status for.

        Returns:
            int: Validation status of the line (VALID, INVALID, WARNING, or COMMENT).
        """
        if 0 <= index < len(self.line_models):
            return self.line_models[index].get_status()
        return self.VALID  # Default to valid if invalid index

    def insert_line(self, line, index):
        """
        Insert a new line at the specified index or at the end of the file.

        Args:
            line (str): The line to insert.
            index (int): The index to insert the line at. If -1, insert at the end.

        Returns:
            bool: True if the line was inserted successfully, False otherwise.
        """
        if index == -1:
            index = len(self.dcfg_file_content)
        self.dcfg_file_content.insert(index, line)  # Insert after current line
        line_model = self._create_line_model(line)

        self.line_models.insert(index, line_model)
        self.current_selected_index = index

        self._record_action('insert', {'position': index, 'line': line})
        return True

    def delete_line(self, index=None):
        """
        Delete the line at specified index or selected position.

        Args:
            index (int, optional): The index of the line to delete. Defaults to None.

        Returns:
            bool: True if the line was deleted successfully, False otherwise.
        """
        if index is None:
            index = self.current_selected_index

        if 0 <= index < len(self.dcfg_file_content):
            deleted_line = self.dcfg_file_content[index]
            self._record_action('delete', {'position': index, 'line': deleted_line})

            # Remove from both content array and line models
            del self.dcfg_file_content[index]
            del self.line_models[index]

            if self.current_selected_index >= len(self.dcfg_file_content):
                self.current_selected_index = len(self.dcfg_file_content) - 1
            return True
        return False

    def edit_current_line(self, new_line):
        """
        Edit the currently selected line.

        Args:
            new_line (str): The new content for the line.

        Returns:
            bool: True if the line was edited successfully, False otherwise.
        """
        index = self.current_selected_index
        if 0 <= index < len(self.dcfg_file_content):
            old_line = self.dcfg_file_content[index]
            self._record_action('edit', {'position': index, 'new_line': new_line, 'old_line': old_line})

            self.dcfg_file_content[index] = new_line
            line_model = self._create_line_model(new_line)
            self.line_models[index] = line_model

            return True
        return False

    def toggle_comment(self):
        """
        Toggle comment on the currently selected line.

        Returns:
            bool: True if the comment was toggled successfully, False otherwise.
        """
        index = self.current_selected_index
        if 0 <= index < len(self.dcfg_file_content):
            line = self.dcfg_file_content[index]

            if line.lstrip().startswith("#"):
                # Uncomment: remove leading "# "
                new_line = line.lstrip("#").lstrip()
                self._record_action('uncomment', {'position': index, 'line': line})
            else:
                # Comment: add "# " to the beginning
                new_line = f"# {line}"
                self._record_action('comment', {'position': index, 'line': line})

            self.dcfg_file_content[index] = new_line

            line_model = self._create_line_model(new_line)

            self.line_models[index] = line_model

            return True
        return False

    def duplicate_line(self):
        """
        Duplicate the currently selected line.

        Returns:
            bool: True if the line was duplicated successfully, False otherwise.
        """
        index = self.current_selected_index
        if 0 <= index < len(self.dcfg_file_content):
            line = self.dcfg_file_content[index]
            self.dcfg_file_content.insert(index + 1, line)

            line_model = self._create_line_model(line)
            self.line_models.insert(index + 1, line_model)

            self._record_action('duplicate', {'position': index, 'line': line})
            # Update the current selected index to the duplicated line
            self.current_selected_index = index + 1

            return True
        return False

    def move_line_up(self):
        """
        Move the currently selected line up one position.

        Returns:
            bool: True if the line was moved successfully, False otherwise.
        """
        index = self.current_selected_index
        if index <= 0 or index >= len(self.dcfg_file_content):
            return False

        self._swap_lines(index, index - 1)
        self.current_selected_index = index - 1

        self._record_action('move_up', {'position': index})
        return True

    def move_line_down(self):
        """
        Move the currently selected line down one position.

        Returns:
            bool: True if the line was moved successfully, False otherwise.
        """
        index = self.current_selected_index
        if index < 0 or index >= len(self.dcfg_file_content) - 1:
            return False

        self._swap_lines(index, index + 1)
        self.current_selected_index = index + 1

        self._record_action('move_down', {'position': index})
        return True


    def find_matches(self, line):
        """
        Find matches for a line using the pattern matcher.

        Args:
            line (str): The line to find matches for.

        Returns:
            tuple: A tuple containing two lists - net matches and template matches.
        """
        if not line or line.startswith('#'):
            return [], []

        fields = self.pattern_matcher.parse_line(line)
        if not fields:
            return [], []

        template = fields.get('template', '')
        net = fields.get('net', '')
        template_regex = fields.get('template_regex', False)
        net_regex = fields.get('net_regex', False)

        return self.pattern_matcher.find_matches(
            template, net, template_regex, net_regex
        )

    def _record_action(self, action_type, data):
        """
        Record an action for undo functionality.

        Args:
            action_type (str): The type of action performed.
            data (dict): The data associated with the action.
        """
        self.action_history.append((action_type, data))
        # Limit history size
        if len(self.action_history) > self.max_history:
            self.action_history.pop(0)

    def undo_last_action(self):
        """
        Undo the last action if available.

        Returns:
            bool: True if the action was undone successfully, False otherwise.
        """
        if not self.action_history:
            return False
        # Get the last action
        action_type, data = self.action_history.pop()
        self.redo_history.append((action_type, data))

        if action_type == 'insert':
            # For insert, we need to delete the line
            position = data['position']
            if 0 <= position < len(self.dcfg_file_content):
                # Delete line from both content and line models
                del self.dcfg_file_content[position]
                del self.line_models[position]

                self.current_selected_index = max(0, position - 1) if self.dcfg_file_content else -1
                return True

        elif action_type == 'delete':
            # For delete, we need to insert the line back
            position = data['position']
            line = data['line']
            if position <= len(self.dcfg_file_content):
                self.dcfg_file_content.insert(position, line)
                line_model = self._create_line_model(line)

                self.line_models.insert(position, line_model)
                self.current_selected_index = position
                return True

        elif action_type == 'comment':
            # For comment, we need to uncomment the line
            position = data['position']
            original_line = data['line']
            if 0 <= position < len(self.dcfg_file_content):
                # Restore the original line (uncomment)
                self.dcfg_file_content[position] = original_line
                line_model = self._create_line_model(original_line)

                self.line_models[position] = line_model
                self.current_selected_index = position
                return True

        elif action_type == 'uncomment':
            # For uncomment, we need to comment the line
            position = data['position']
            commented_line = data['line']
            if 0 <= position < len(self.dcfg_file_content):
                # Restore the commented line
                self.dcfg_file_content[position] = commented_line
                line_model = self._create_line_model(commented_line)

                self.line_models[position] = line_model
                self.current_selected_index = position
                return True

        elif action_type == 'edit':
            # For edit, we need to restore the old line
            position = data['position']
            old_line = data['old_line']
            if 0 <= position < len(self.dcfg_file_content):
                self.dcfg_file_content[position] = old_line
                line_model = self._create_line_model(old_line)

                self.line_models[position] = line_model

                return True

        elif action_type == 'duplicate':
            # For duplicate, we need to delete the duplicated line
            position = data['position'] + 1  # Duplicate is always inserted after original
            if 0 <= position < len(self.dcfg_file_content):
                # Remove duplicated line from both arrays
                del self.dcfg_file_content[position]
                del self.line_models[position]

                self.current_selected_index = data['position']
                return True
        
        elif action_type == 'move_up':
            # For move_up, we need to swap the lines back
            position = data['position']
            if 0 < position < len(self.dcfg_file_content):
                self._swap_lines(position, position - 1)
                self.current_selected_index = position

                return True
            
        elif action_type == 'move_down':
            # For move_down, we need to swap the lines back
            position = data['position']
            if 0 <= position < len(self.dcfg_file_content) - 1:
                self._swap_lines(position, position + 1)
                self.current_selected_index = position

                return True


        return False

    def redo_action(self):
        """
        Redo the last action if available.

        Returns:
            bool: True if the action was redone successfully, False otherwise.
        """
        if not self.redo_history:
            return False
        # Get the last action
        action_type, data = self.redo_history.pop()
        self.action_history.append((action_type, data))

        if action_type == 'insert':
            # For insert, we need to insert the line back
            position = data['position']
            line = data['line']

            if position <= len(self.dcfg_file_content):
                self.dcfg_file_content.insert(position, line)
                line_model = self._create_line_model(line)

                self.line_models.insert(position, line_model)
                self.current_selected_index = position
                return True

        elif action_type == 'delete':
            # For delete, we need to delete the line
            position = data['position']
            if 0 <= position < len(self.dcfg_file_content):
                # Delete from both arrays
                del self.dcfg_file_content[position]
                del self.line_models[position]

                self.current_selected_index = max(0, position - 1) if self.dcfg_file_content else -1
                return True

        elif action_type == 'comment':
            # For comment, we need to comment the line again
            position = data['position']
            original_line = data['line']
            if 0 <= position < len(self.dcfg_file_content):
                # Add comment prefix
                commented_line = f"# {original_line}"
                self.dcfg_file_content[position] = commented_line
                line_model = self._create_line_model(commented_line)

                self.line_models[position] = line_model
                self.current_selected_index = position
                return True

        elif action_type == 'uncomment':
            # For uncomment, we need to uncomment the line again
            position = data['position']
            commented_line = data['line']
            if 0 <= position < len(self.dcfg_file_content):
                if commented_line.startswith("#"):
                    # Remove leading "# "
                    uncommented_line = commented_line.lstrip("#").lstrip()
                else:
                    # This shouldn't happen, but just in case
                    uncommented_line = commented_line

                self.dcfg_file_content[position] = uncommented_line
                line_model = self._create_line_model(uncommented_line)

                self.line_models[position] = line_model
                self.current_selected_index = position
                return True

        elif action_type == 'edit':
            # For edit, we need to update the line
            position = data['position']
            new_line = data['new_line']

            if 0 <= position < len(self.dcfg_file_content):
                self.dcfg_file_content[position] = new_line
                line_model = self._create_line_model(new_line)
                self.line_models[position] = line_model
                return True

        elif action_type == 'duplicate':
            # For duplicate, we need to re-insert the duplicated line
            position = data['position']
            line = data['line']

            if 0 <= position < len(self.dcfg_file_content):
                self.dcfg_file_content.insert(position + 1, line)
                line_model = self._create_line_model(line)

                self.line_models.insert(position + 1, line_model)
                self.current_selected_index = position + 1

                return True

        elif action_type == 'move_up':
            # For move_up, we need to swap the lines back
            position = data['position']
            if 0 < position < len(self.dcfg_file_content):
                self._swap_lines(position, position - 1)
                self.current_selected_index = position

                return True
            
        elif action_type == 'move_down':
            # For move_down, we need to swap the lines back
            position = data['position']
            if 0 <= position < len(self.dcfg_file_content) - 1:
                self._swap_lines(position, position + 1)
                self.current_selected_index = position

                return True

        return False

    def save_to_file(self):
        """
        Save updated file.

        Returns:
            bool: True if the file was saved successfully, False otherwise.
        """
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
        """
        Check if there are unsaved changes.

        Returns:
            bool: True if there are unsaved changes, False otherwise.
        """
        return self.dcfg_file_content != self.original_content

    def set_selected_index(self, index):
        """
        Set the currently selected line index.

        Args:
            index (int): The index to set as the currently selected line.

        Returns:
            bool: True if the index was set successfully, False otherwise.
        """
        if 0 <= index < len(self.dcfg_file_content):
            self.current_selected_index = index
            return True
        return False

    def _swap_lines(self, index, other_index):
        """
        Swaps two lines in the model
        """
        # Swap lines
        self.dcfg_file_content[index], self.dcfg_file_content[other_index] = \
            self.dcfg_file_content[other_index], self.dcfg_file_content[index]
        # Swap line models
        self.line_models[index], self.line_models[other_index] = \
            self.line_models[other_index], self.line_models[index]
