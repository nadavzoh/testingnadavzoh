class AbstractDialogModel:
    """
    Abstract base class for all dialog models in the Lotus application.
    Each dialog model should implement this interface.
    """

    def validate_input(self):
        """Validate the current input data."""
        raise NotImplementedError("Subclasses must implement validate_input")

    def format_line(self):
        """Format the model data as a line to be inserted/edited in the config file."""
        raise NotImplementedError("Subclasses must implement format_line")

    def get_fields_from_line(self, line):
        """Parse a config line into fields the model can understand."""
        raise NotImplementedError("Subclasses must implement get_fields_from_line")