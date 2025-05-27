from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from src.core.models.LineModelInterface import LineModelInterface


class LineModelFactory(ABC):
    """
    Abstract factory for creating line models.
    
    This class follows the Factory pattern to create line model instances based on content.
    Concrete implementations should override the create_line_model method to return
    the appropriate line model type.
    """
    
    @abstractmethod
    def create_line_model(self, line_content: str) -> LineModelInterface:
        """
        Create a new line model instance.
        
        Args:
            line_content: The content of the line
            
        Returns:
            LineModelInterface: A new line model instance
        """
        pass


class LineModelRegistry:
    """
    Registry for line model factories.
    
    This class maintains a registry of line model factories that can be used
    to create different types of line models based on file type or other criteria.
    It follows the Service Locator pattern to provide a central point for accessing
    line model factories.
    """
    
    def __init__(self):
        """Initialize the registry."""
        self._factories = {}
    
    def register_factory(self, file_type: str, factory: LineModelFactory) -> None:
        """
        Register a factory for a specific file type.
        
        Args:
            file_type: The file type (e.g., 'af', 'mutex')
            factory: The factory to register
        """
        self._factories[file_type] = factory
    
    def get_factory(self, file_type: str) -> LineModelFactory:
        """
        Get a factory for a specific file type.
        
        Args:
            file_type: The file type
            
        Returns:
            LineModelFactory: The factory for the specified file type,
                             or None if no factory is registered
        """
        return self._factories.get(file_type)
    
    def get_available_file_types(self) -> list:
        """
        Get a list of file types for which factories are registered.
        
        Returns:
            list: A list of file types
        """
        return list(self._factories.keys())
