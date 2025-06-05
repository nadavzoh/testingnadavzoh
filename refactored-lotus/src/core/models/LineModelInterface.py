from abc import ABC, abstractmethod
from typing import List, Optional


class LineModelInterface(ABC):
    """
    Interface for line models.
    
    This abstract base class defines the interface that all line models must implement.
    It provides methods for line validation, status checks, and data access.
    
    Attributes:
        VALID (int): Line is valid
        INVALID (int): Line is invalid
        WARNING (int): Line has a warning
        COMMENT (int): Line is a comment
    """
    
    # Line validation status constants
    UN_INITIALIZED = -1
    VALID = 0
    INVALID = 1
    WARNING = 2
    COMMENT = 3
    
    @abstractmethod
    def __init__(self, line_content: str):
        """
        Initialize the line model with the given content.
        
        Args:
            line_content: The content of the line
        """
        pass
    
    @abstractmethod
    def get_content(self) -> str:
        """
        Get the line content.
        
        Returns:
            str: The content of the line
        """
        pass
    
    @abstractmethod
    def set_content(self, content: str) -> None:
        """
        Set the line content.
        
        Args:
            content: The new content for the line
        """
        pass
    
    @abstractmethod
    def get_status(self) -> int:
        """
        Get the validation status of the line.
        
        Returns:
            int: The validation status (VALID, INVALID, WARNING, or COMMENT)
        """
        pass
    
    @abstractmethod
    def validate(self) -> int:
        """
        Validate the line content.
        
        Returns:
            int: The validation status (VALID, INVALID, WARNING, or COMMENT)
        """
        pass
    
    @abstractmethod
    def is_comment(self) -> bool:
        """
        Check if the line is a comment.
        
        Returns:
            bool: True if the line is a comment, False otherwise
        """
        pass
