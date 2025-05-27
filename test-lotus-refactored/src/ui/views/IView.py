from abc import abstractmethod
from typing import Optional, List, Any

class IView:
    """
    Interface for all views in the application.
    
    This class defines the interface that all views must implement.
    It ensures consistent behavior across different views.
    """
    
    @abstractmethod
    def show(self) -> None:
        """Show the view."""
        pass
    
    @abstractmethod
    def hide(self) -> None:
        """Hide the view."""
        pass
    
    @abstractmethod
    def set_title(self, title: str) -> None:
        """
        Set the title of the view.
        
        Args:
            title: The title to set
        """
        pass
