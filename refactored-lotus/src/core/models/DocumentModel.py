from typing import List, Type, Dict, Any, Tuple, Optional
import os
from src.core.models.LineModelFactory import LineModelFactory

class DocumentModel:
    """
    Model representing a text document with line-based operations.
    
    This class manages document state and provides methods for manipulating
    text content on a line-by-line basis, with a clean separation of concerns.
    Follows the Model in the MVP pattern, with no UI dependencies.
    """
    
    # Action types for history
    ACTION_INSERT = 'insert'
    ACTION_DELETE = 'delete'
    ACTION_EDIT = 'edit'
    ACTION_COMMENT = 'comment'
    ACTION_UNCOMMENT = 'uncomment'
    ACTION_MOVE = 'move'
    ACTION_DUPLICATE = 'duplicate'
    
    def __init__(self, line_model_factory: LineModelFactory = None, comment_indicator: str = '#'):
        """
        Initialize the document model.
        
        Args:
            line_model_factory: Factory for creating line model instances
        """
        self._file_path = ""
        self._content = []
        self._original_content = []
        self._line_models = []
        self._line_model_factory = line_model_factory
        self._comment_indicator = comment_indicator
        self._selected_index = -1
        self._modified = False
        
        # History for undo/redo
        self._action_history = []
        self._redo_history = []
        self._max_history = 50
    
    def load_file(self, file_path: str) -> bool:
        """
        Load content from a file.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            bool: True if the file was loaded successfully, False otherwise
        """
        if not os.path.exists(file_path):
            return False
            
        try:
            with open(file_path, 'r') as file:
                self._content = [line.rstrip('\n') for line in file.readlines()]
            
            self._file_path = file_path
            self._original_content = self._content.copy()
            self._modified = False
            
            # Create line models if factory is available
            if self._line_model_factory:
                self._create_line_models()
            
            # Clear history when loading a new file
            self._action_history.clear()
            self._redo_history.clear()
            
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def save_file(self, file_path: Optional[str] = None) -> bool:
        """
        Save content to a file.
        
        Args:
            file_path: Path to save the file to. If None, use the current file path.
            
        Returns:
            bool: True if the file was saved successfully, False otherwise
        """
        path = file_path if file_path else self._file_path
        if not path:
            return False
            
        try:
            with open(path, 'w') as file:
                file.write('\n'.join(self._content))
            
            # Update the file path if a new one was provided
            if file_path:
                self._file_path = file_path
            
            # Update original content after save
            self._original_content = self._content.copy()
            
            # Reset the modified flag since changes have been saved
            self._modified = False

            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    def has_unsaved_changes(self) -> bool:
        """
        Check if the document has unsaved changes.
        
        Returns:
            bool: True if there are unsaved changes, False otherwise
        """
        return self._content != self._original_content
    
    def get_file_path(self) -> str:
        """
        Get the current file path.
        
        Returns:
            str: The current file path
        """
        return self._file_path
    
    def set_file_path(self, file_path: str) -> None:
        """
        Set the file path.
        
        Args:
            file_path: The new file path
        """
        self._file_path = file_path
    
    def get_line_count(self) -> int:
        """
        Get the number of lines in the document.
        
        Returns:
            int: The number of lines
        """
        return len(self._content)
    
    def get_line(self, index: int) -> Optional[str]:
        """
        Get a line by index.
        
        Args:
            index: Index of the line to get
            
        Returns:
            str: The line at the specified index, or None if index is out of bounds
        """
        if 0 <= index < len(self._content):
            return self._content[index]
        return None
    
    def get_all_lines(self) -> List[str]:
        """
        Get all lines in the document.
        
        Returns:
            List[str]: All lines in the document
        """
        return self._content.copy()
    
    def get_content(self) -> List[str]:
        return self._content.copy()
    
    def get_selected_index(self) -> int:
        """
        Get the index of the currently selected line.
        
        Returns:
            int: The index of the selected line, or -1 if no line is selected
        """
        return self._selected_index
    
    def set_selected_index(self, index: int) -> None:
        """
        Set the index of the currently selected line.
        
        Args:
            index: The index to select
        """
        if index < -1:
            index = -1
        elif index >= len(self._content):
            index = len(self._content) - 1
            
        if index != self._selected_index:
            self._selected_index = index
    
    def get_line_model(self, index: int) -> Any:
        """
        Get a line model by index.
        
        Args:
            index: Index of the line model to get
            
        Returns:
            The line model at the specified index, or None if index is out of bounds
            or no line model factory is set
        """
        if not self._line_model_factory or not (0 <= index < len(self._line_models)):
            return None
        return self._line_models[index]
    
    
    def insert_line(self, line: str, index: int = -1) -> bool:
        """
        Insert a line at the specified index.
        
        Args:
            line: The line to insert
            index: The index to insert the line at. If -1, insert at the end.
            
        Returns:
            bool: True if the line was inserted successfully
        """
        # If index is -1, insert at the end
        if index == -1:
            index = len(self._content)
        
        # Insert the line
        self._content.insert(index, line)
        
        # Create and insert line model if factory is available
        if self._line_model_factory:
            line_model = self._line_model_factory.create_line_model(line)
            self._line_models.insert(index, line_model)
        
        # Record action for undo
        self._record_action(self.ACTION_INSERT, {'index': index, 'line': line})
        
        # Update selection and mark document as modified
        self.set_selected_index(index)
        self._modified = True
        
        return True
    
    def delete_line(self, index: Optional[int] = None) -> bool:
        """
        Delete a line at the specified index.
        
        Args:
            index: The index of the line to delete. If None, use the selected index.
            
        Returns:
            bool: True if the line was deleted successfully, False otherwise
        """
        if index is None:
            index = self._selected_index
        
        if not (0 <= index < len(self._content)):
            return False
        
        # Record action for undo
        deleted_line = self._content[index]
        self._record_action(self.ACTION_DELETE, {'index': index, 'line': deleted_line})
        
        # Delete the line
        del self._content[index]
        
        # Delete line model if factory is available
        if self._line_model_factory and 0 <= index < len(self._line_models):
            del self._line_models[index]
        
        # Update selection
        if self._selected_index >= len(self._content):
            self.set_selected_index(len(self._content) - 1)
        
        # Mark document as modified
        self._modified = True
        
        return True
    
    def edit_line(self, new_line: str, index: Optional[int] = None) -> bool:
        """
        Edit a line at the specified index.
        
        Args:
            new_line: The new content for the line
            index: The index of the line to edit. If None, use the selected index.
            
        Returns:
            bool: True if the line was edited successfully, False otherwise
        """
        if index is None:
            index = self._selected_index
        
        if not (0 <= index < len(self._content)):
            return False
        
        # Record action for undo
        old_line = self._content[index]
        self._record_action(self.ACTION_EDIT, {
            'index': index, 
            'old_line': old_line, 
            'new_line': new_line
        })
        
        # Update the line
        self._content[index] = new_line
        
        # Update line model if factory is available
        if self._line_model_factory:
            line_model = self._line_model_factory.create_line_model(new_line)
            self._line_models[index] = line_model
        
        # Mark document as modified
        self._modified = True
        
        return True
    
    def toggle_comment(self, index: Optional[int] = None) -> bool:
        """
        Toggle comment status on a line.
        
        Args:
            index: The index of the line to toggle. If None, use the selected index.
            
        Returns:
            bool: True if the comment was toggled successfully, False otherwise
        """
        if index is None:
            index = self._selected_index
        
        if not (0 <= index < len(self._content)):
            return False
        
        line = self._content[index]
        
        if line.lstrip().startswith(self._comment_indicator):
            # Uncomment: remove the comment marker
            new_line = line.lstrip(self._comment_indicator).lstrip()
            action_type = self.ACTION_UNCOMMENT
        else:
            # Comment: add a comment marker
            new_line = f"{self._comment_indicator} {line}"
            action_type = self.ACTION_COMMENT
        
        # Record action for undo
        self._record_action(action_type, {'index': index, 'line': line})
        
        # Update the line
        self._content[index] = new_line
        
        # Update line model if factory is available
        if self._line_model_factory:
            line_model = self._line_model_factory.create_line_model(new_line)
            self._line_models[index] = line_model
        
        # Mark document as modified
        self._modified = True
        
        return True
    
    def duplicate_line(self, index: Optional[int] = None) -> bool:
        """
        Duplicate a line.
        
        Args:
            index: The index of the line to duplicate. If None, use the selected index.
            
        Returns:
            bool: True if the line was duplicated successfully, False otherwise
        """
        if index is None:
            index = self._selected_index
        
        if not (0 <= index < len(self._content)):
            return False
        
        line = self._content[index]
        
        # Record action for undo
        self._record_action(self.ACTION_DUPLICATE, {'index': index, 'line': line})
        
        # Insert the duplicated line after the original
        self._content.insert(index + 1, line)
        
        # Create and insert line model if factory is available
        if self._line_model_factory:
            # line_model = self._line_model_factory.create_line_model(line)
            # self._line_models.insert(index + 1, line_model)
            line_model = self._line_model_factory.create_line_model_copy(self._line_models[index]) if self._line_models else None
            if line_model:
                self._line_models.insert(index + 1, line_model)
        
        # Update selection and mark as modified
        self.set_selected_index(index + 1)
        self._modified = True
        
        return True
    
    def move_line_up(self, index: Optional[int] = None) -> bool:
        """
        Move a line up one position.
        
        Args:
            index: The index of the line to move. If None, use the selected index.
            
        Returns:
            bool: True if the line was moved successfully, False otherwise
        """
        if index is None:
            index = self._selected_index
        
        if not (0 < index < len(self._content)):
            return False
        
        # Record action for undo
        self._record_action(self.ACTION_MOVE, {
            'from_index': index, 
            'to_index': index - 1
        })
        
        # Swap lines
        self._content[index], self._content[index - 1] = self._content[index - 1], self._content[index]
        
        # Swap line models if factory is available
        if self._line_model_factory and len(self._line_models) > index:
            self._line_models[index], self._line_models[index - 1] = self._line_models[index - 1], self._line_models[index]
        
        # Update selection and mark as modified
        self.set_selected_index(index - 1)
        self._modified = True
        
        return True
    
    def move_line_down(self, index: Optional[int] = None) -> bool:
        """
        Move a line down one position.
        
        Args:
            index: The index of the line to move. If None, use the selected index.
            
        Returns:
            bool: True if the line was moved successfully, False otherwise
        """
        if index is None:
            index = self._selected_index
        
        if not (0 <= index < len(self._content) - 1):
            return False
        
        # Record action for undo
        self._record_action(self.ACTION_MOVE, {
            'from_index': index, 
            'to_index': index + 1
        })
        
        # Swap lines
        self._content[index], self._content[index + 1] = self._content[index + 1], self._content[index]
        
        # Swap line models if factory is available
        if self._line_model_factory and len(self._line_models) > index + 1:
            self._line_models[index], self._line_models[index + 1] = self._line_models[index + 1], self._line_models[index]
        
        # Update selection and mark as modified
        self.set_selected_index(index + 1)
        self._modified = True
        
        return True
    
    def can_undo(self) -> bool:
        """
        Check if there are actions that can be undone.
        
        Returns:
            bool: True if there are actions that can be undone, False otherwise
        """
        return len(self._action_history) > 0
    
    def can_redo(self) -> bool:
        """
        Check if there are actions that can be redone.
        
        Returns:
            bool: True if there are actions that can be redone, False otherwise
        """
        return len(self._redo_history) > 0
    
    def undo(self) -> bool:
        """
        Undo the last action.
        
        Returns:
            bool: True if an action was undone, False otherwise
        """
        if not self._action_history:
            return False
        
        # Get the last action
        action = self._action_history.pop()
        action_type = action['type']
        data = action['data']
        
        # Add to redo history
        self._redo_history.append(action)
        
        # Perform the undo based on action type
        if action_type == self.ACTION_INSERT:
            index = data['index']
            self._content.pop(index)
            if self._line_model_factory and len(self._line_models) > index:
                self._line_models.pop(index)
        
        elif action_type == self.ACTION_DELETE:
            index = data['index']
            line = data['line']
            self._content.insert(index, line)
            if self._line_model_factory:
                line_model = self._line_model_factory.create_line_model(line)
                self._line_models.insert(index, line_model)
        
        elif action_type == self.ACTION_EDIT:
            index = data['index']
            old_line = data['old_line']
            self._content[index] = old_line
            if self._line_model_factory:
                line_model = self._line_model_factory.create_line_model(old_line)
                self._line_models[index] = line_model
        
        elif action_type in (self.ACTION_COMMENT, self.ACTION_UNCOMMENT):
            index = data['index']
            line = data['line']
            self._content[index] = line
            if self._line_model_factory:
                line_model = self._line_model_factory.create_line_model(line)
                self._line_models[index] = line_model
        
        elif action_type == self.ACTION_MOVE:
            from_index = data['from_index']
            to_index = data['to_index']
            # Swap lines back
            self._content[from_index], self._content[to_index] = self._content[to_index], self._content[from_index]
            if self._line_model_factory:
                self._line_models[from_index], self._line_models[to_index] = self._line_models[to_index], self._line_models[from_index]
        
        elif action_type == self.ACTION_DUPLICATE:
            index = data['index']
            self._content.pop(index + 1)
            if self._line_model_factory and len(self._line_models) > index + 1:
                self._line_models.pop(index + 1)
        
        self._modified = False if len(self._action_history) == 0 else True
        
        return True
    
    def redo(self) -> bool:
        """
        Redo the last undone action.
        
        Returns:
            bool: True if an action was redone, False otherwise
        """
        if not self._redo_history:
            return False
        
        # Get the last undone action
        action = self._redo_history.pop()
        action_type = action['type']
        data = action['data']
        
        # Add to undo history
        self._action_history.append(action)
        
        # Perform the redo based on action type
        if action_type == self.ACTION_INSERT:
            index = data['index']
            line = data['line']
            self._content.insert(index, line)
            if self._line_model_factory:
                line_model = self._line_model_factory.create_line_model(line)
                self._line_models.insert(index, line_model)
        
        elif action_type == self.ACTION_DELETE:
            index = data['index']
            self._content.pop(index)
            if self._line_model_factory and len(self._line_models) > index:
                self._line_models.pop(index)
        
        elif action_type == self.ACTION_EDIT:
            index = data['index']
            new_line = data['new_line']
            self._content[index] = new_line
            if self._line_model_factory:
                line_model = self._line_model_factory.create_line_model(new_line)
                self._line_models[index] = line_model
        
        elif action_type == self.ACTION_COMMENT:
            index = data['index']
            line = data['line']
            self._content[index] = f"# {line}"
            if self._line_model_factory:
                line_model = self._line_model_factory.create_line_model(f"# {line}")
                self._line_models[index] = line_model
        
        elif action_type == self.ACTION_UNCOMMENT:
            index = data['index']
            line = data['line']
            new_line = line.lstrip('#').lstrip()
            self._content[index] = new_line
            if self._line_model_factory:
                line_model = self._line_model_factory.create_line_model(new_line)
                self._line_models[index] = line_model
        
        elif action_type == self.ACTION_MOVE:
            from_index = data['from_index']
            to_index = data['to_index']
            # Swap lines
            self._content[from_index], self._content[to_index] = self._content[to_index], self._content[from_index]
            if self._line_model_factory:
                self._line_models[from_index], self._line_models[to_index] = self._line_models[to_index], self._line_models[from_index]
        
        elif action_type == self.ACTION_DUPLICATE:
            index = data['index']
            line = data['line']
            self._content.insert(index + 1, line)
            if self._line_model_factory:
                line_model = self._line_model_factory.create_line_model(line)
                self._line_models.insert(index + 1, line_model)
        
        # Mark document as modified
        self._modified = True
        
        return True
    
    def _record_action(self, action_type: str, data: Dict[str, Any]) -> None:
        """
        Record an action for undo/redo.
        
        Args:
            action_type: The type of action
            data: The data associated with the action
        """
        self._action_history.append({
            'type': action_type,
            'data': data
        })
        
        # Clear redo history when a new action is performed
        self._redo_history.clear()
        
        # Limit history size
        if len(self._action_history) > self._max_history:
            self._action_history.pop(0)
    
    def _create_line_models(self) -> None:
        """
        Create line models for all content lines.
        """
        if not self._line_model_factory:
            return
            
        self._line_models = []
        for line in self._content:
            line_model = self._line_model_factory.create_line_model(line)
            self._line_models.append(line_model)
    
    def set_line_model_factory(self, factory) -> None:
        """
        Set the factory for creating line models.
        
        Args:
            factory: The factory to use
        """
        self._line_model_factory = factory
        
        # Recreate line models if we have content
        if self._content:
            self._create_line_models()