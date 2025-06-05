from typing import Optional

from src.core.models.DocumentModel import DocumentModel
from src.core.models.LineModelFactory import LineModelFactory, LineModelRegistry


class DocumentModelFactory:
    """
    Factory for creating document model instances.
    
    This class is responsible for creating document model instances with the
    appropriate line model factory based on the file type.
    """
    
    def __init__(self, line_model_registry: Optional[LineModelRegistry] = None):
        """
        Initialize the document model factory.
        
        Args:
            line_model_registry: Registry of line model factories
        """
        self._line_model_registry = line_model_registry or LineModelRegistry()
    
    def create_document_model(self, file_type: Optional[str] = None, comment_indicator: str = "#") -> DocumentModel:
        """
        Create a new document model instance.
        
        Args:
            file_type: The type of file the document model will handle
                      (e.g., 'af', 'mutex', 'text')
                      
        Returns:
            DocumentModel: A new document model instance with the appropriate
                          line model factory
        """
        line_model_factory = None
        
        if file_type:
            line_model_factory = self._line_model_registry.get_factory(file_type)

        
        return DocumentModel(line_model_factory, comment_indicator)
    
    def get_line_model_registry(self) -> LineModelRegistry:
        """
        Get the line model registry used by this factory.
        
        Returns:
            LineModelRegistry: The line model registry
        """
        return self._line_model_registry
    
    def set_line_model_registry(self, registry: LineModelRegistry) -> None:
        """
        Set the line model registry.
        
        Args:
            registry: The new line model registry
        """
        self._line_model_registry = registry
