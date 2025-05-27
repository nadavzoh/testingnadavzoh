from abc import abstractmethod
from typing import Optional, List, Any

from src.ui.views.IView import IView


class IDocumentView(IView):
    """
    Interface for document view.
    
    This interface extends the base view interface with document-specific methods.
    It defines the contract that document views must fulfill.
    """
    
    @abstractmethod
    def set_content(self, content: List[str]) -> None:
        """
        Set the content of the document view.
        
        Args:
            content: The content as a list of strings
        """
        pass
    
    @abstractmethod
    def get_selected_index(self) -> int:
        """
        Get the index of the currently selected line.
        
        Returns:
            int: The index of the selected line, or -1 if no line is selected
        """
        pass
    
    @abstractmethod
    def set_selected_index(self, index: int) -> None:
        """
        Set the index of the selected line.
        
        Args:
            index: The index to select
        """
        pass
    
    @abstractmethod
    def update_line(self, index: int, content: str) -> None:
        """
        Update a line in the view.
        
        Args:
            index: The index of the line to update
            content: The new content for the line
        """
        pass
