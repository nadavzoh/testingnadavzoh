from src.core.models.LineModelFactory import LineModelFactory
from src.core.models.AfLineModel import AfLineModel


class AfLineModelFactory(LineModelFactory):
    """
    Factory for creating AF line model instances.
    
    This class implements the LineModelFactory interface to create
    AfLineModel instances for Activity Factor configuration files.
    """
    
    def create_line_model(self, line_content: str) -> AfLineModel:
        """
        Create a new AfLineModel instance.
        
        Args:
            line_content: The content of the line
            
        Returns:
            LineModelInterface: A new AfLineModel instance
        """
        model = AfLineModel(line_content)
                     
        return model

    def create_line_model_copy(self, line_model: AfLineModel) -> AfLineModel:
        """
        Create a deep copy of an existing AfLineModel instance.
        Args:
            line_model: The AfLineModel instance to copy
        Returns:
            AfLineModel: A new AfLineModel instance with the same content
        """
        if not isinstance(line_model, AfLineModel):
            raise TypeError("Expected an instance of AfLineModel")
        
        # Create a new instance with the same content
        return AfLineModel(line_model.get_content())  

