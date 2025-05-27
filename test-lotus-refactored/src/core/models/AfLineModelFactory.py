from src.core.models.LineModelFactory import LineModelFactory
from src.core.models.AfLineModel import AfLineModel
from src.core.models.LineModelInterface import LineModelInterface


class AfLineModelFactory(LineModelFactory):
    """
    Factory for creating AF line model instances.
    
    This class implements the LineModelFactory interface to create
    AfLineModel instances for Activity Factor configuration files.
    """
    
    def create_line_model(self, line_content: str) -> LineModelInterface:
        """
        Create a new AfLineModel instance.
        
        Args:
            line_content: The content of the line
            
        Returns:
            LineModelInterface: A new AfLineModel instance
        """
        return AfLineModel(line_content)
