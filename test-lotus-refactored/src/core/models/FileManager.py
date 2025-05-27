import os
from typing import List, Optional, Dict, Tuple


class FileManager:
    """
    Manager for file operations.
    
    This class provides methods for loading, saving, and checking files.
    It is decoupled from the document model to ensure separation of concerns.
    """
    
    def __init__(self):
        """Initialize the file manager."""
        self._known_file_types = {
            ".af.dcfg": "af",
            ".mutex.dcfg": "mutex",
            ".txt": "text",
            ".log": "text"
        }
    
    def load_file(self, file_path: str) -> Tuple[bool, List[str], Optional[str]]:
        """
        Load a file and return its contents.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            Tuple containing:
            - bool: Whether the file was loaded successfully
            - List[str]: The file contents as a list of lines
            - Optional[str]: Error message if loading failed, or None
        """
        if not os.path.exists(file_path):
            return False, [], f"File not found: {file_path}"
        
        try:
            with open(file_path, 'r') as file:
                content = [line.rstrip('\n') for line in file.readlines()]
            return True, content, None
        except Exception as e:
            return False, [], f"Error loading file: {str(e)}"
    
    def save_file(self, file_path: str, content: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Save content to a file.
        
        Args:
            file_path: Path to save the file to
            content: Content to save
            
        Returns:
            Tuple containing:
            - bool: Whether the file was saved successfully
            - Optional[str]: Error message if saving failed, or None
        """
        try:
            with open(file_path, 'w') as file:
                file.write('\n'.join(content))
            return True, None
        except Exception as e:
            return False, f"Error saving file: {str(e)}"
    
    def get_file_type(self, file_path: str) -> Optional[str]:
        """
        Get the type of a file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Optional[str]: The file type, or None if the file type is not recognized
        """
        # Get the file extension
        _, ext = os.path.splitext(file_path)
        
        # Handle special cases like .af.dcfg
        for pattern, file_type in self._known_file_types.items():
            if file_path.endswith(pattern):
                return file_type
        
        # Return None for unknown file types
        return None
    
    def register_file_type(self, extension: str, file_type: str) -> None:
        """
        Register a new file type.
        
        Args:
            extension: The file extension (e.g., '.af.dcfg')
            file_type: The file type (e.g., 'af')
        """
        self._known_file_types[extension] = file_type
