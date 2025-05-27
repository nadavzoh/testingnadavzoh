class AbstractDialogModel:
    """
    Abstract base class for all dialog models in the Lotus application.

    This class defines the interface that all dialog models must implement to ensure
    consistent behavior across different dialog types. Dialog models are responsible
    for storing, validating, and formatting dialog data.

    Dialog models work with their corresponding controllers and views to implement
    the Model-View-Controller pattern, maintaining separation of concerns in the UI.
    """

    def validate_input(self):
        """
        Validate the current input data stored in the model.

        This method should check all fields for validity according to specified rules
        and data constraints specific to each dialog type.

        Returns:
            bool: True if all inputs are valid

        Raises:
            ValueError: With descriptive message if validation fails
        """
        raise NotImplementedError("Subclasses must implement validate_input")

    def format_line(self):
        """
        Format the model data as a line to be inserted or edited in the config file.

        This method transforms the internal model state into a properly formatted
        line according to the specific syntax rules for the configuration file.

        Returns:
            str: Formatted line ready to be inserted into the configuration file
        """
        raise NotImplementedError("Subclasses must implement format_line")

    def get_fields_from_line(self, line):
        """
        Parse a configuration line into fields the model can understand.

        This method does the reverse of format_line(), taking a line from the
        configuration file and splitting it into meaningful fields.

        Args:
            line (str): The line to parse from the configuration file

        Returns:
            dict: Dictionary containing the parsed fields

        Raises:
            ValueError: If the line format is invalid
        """
        raise NotImplementedError("Subclasses must implement get_fields_from_line")