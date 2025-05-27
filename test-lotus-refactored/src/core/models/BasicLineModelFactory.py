from src.core.models.LineModelFactory import LineModelFactory
from src.core.models.BasicLineModel import BasicLineModel
from src.core.models.LineModelInterface import LineModelInterface


class BasicLineModelFactory(LineModelFactory):
    """
    Factory for creating basic line model instances.
    
    This class implements the LineModelFactory interface to create
    BasicLineModel instances.
    """
    
    def create_line_model(self, line_content: str) -> LineModelInterface:
        """
        Create a new BasicLineModel instance.
        
        Args:
            line_content: The content of the line
            
        Returns:
            LineModelInterface: A new BasicLineModel instance
        """
        return BasicLineModel(line_content)
