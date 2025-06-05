import re
from typing import List, Optional

from src.core.models.LineModelInterface import LineModelInterface


class BasicLineModel(LineModelInterface):
    """
    Basic implementation of a line model.
    
    This class provides a simple implementation of the LineModelInterface
    with basic validation and no special formatting requirements.
    It can be used as a base class for more specialized line models.
    
    Attributes:
        content (str): The content of the line
        status (int): The validation status of the line
    """
    
    def __init__(self, line_content: str):
        """
        Initialize the line model with the given content.
        
        Args:
            line_content: The content of the line
        """
        self._content = line_content
        self._status = self.validate()
    
    def get_content(self) -> str:
        """
        Get the line content.
        
        Returns:
            str: The content of the line
        """
        return self._content
    
    def set_content(self, content: str) -> None:
        """
        Set the line content.
        
        Args:
            content: The new content for the line
        """
        self._content = content
        self._status = self.validate()
    
    def get_status(self) -> int:
        """
        Get the validation status of the line.
        
        Returns:
            int: The validation status (VALID, INVALID, WARNING, or COMMENT)
        """
        return self._status
    
    def validate(self) -> int:
        """
        Validate the line content.
        
        For the basic line model, all non-empty lines are valid,
        and empty lines are valid but with a warning.
        
        Returns:
            int: The validation status (VALID, INVALID, WARNING, or COMMENT)
        """
        if self.is_comment():
            return self.COMMENT
        elif not self._content.strip():
            return self.WARNING  # Empty lines are valid but with a warning
        return self.VALID
    
    def is_comment(self) -> bool:
        """
        Check if the line is a comment.
        
        Returns:
            bool: True if the line is a comment, False otherwise
        """
        return self._content.strip().startswith('#')
    
    def get_matches(self) -> List[str]:
        """
        Get a list of matches for this line.
        
        For the basic line model, there are no matches.
        
        Returns:
            List[str]: An empty list
        """
        return []
    
    def get_hint(self) -> str:
        """
        Get a hint for this line (e.g., error message).
        
        For the basic line model, the hint is based on the validation status.
        
        Returns:
            str: A hint or error message
        """
        if self._status == self.COMMENT:
            return "Comment line"
        elif self._status == self.WARNING:
            return "Empty line"
        elif self._status == self.INVALID:
            return "Invalid line format"
        return ""
