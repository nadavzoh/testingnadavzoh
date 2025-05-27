from abc import ABC, abstractmethod


class AbstractLineModel(ABC):
    """
    Abstract base class for line models in the document.

    This class provides a foundation for different types of line models in the
    application, allowing the DocumentModel to handle various line types uniformly.
    Each line model represents a single line in a document and manages validation
    status and display properties for that line.

    Line models are responsible for parsing, validating, and providing access to
    the data contained in a single line of text in the document.

    Attributes:
        VALID (int): Status constant for valid lines
        INVALID (int): Status constant for invalid lines
        WARNING (int): Status constant for lines with warnings
        COMMENT (int): Status constant for comment lines

        line (str): The raw text of the line
        status (int): The validation status of the line
        color: The display color for the line
    """
    # Status constants
    VALID = 0
    INVALID = 1
    WARNING = 2
    COMMENT = 3

    def __init__(self, line: str):
        """
        Initialize a line model with the raw line text.

        The constructor automatically validates the line upon creation.

        Args:
            line (str): The raw text of the line
        """
        self.line = line
        self.status = self.validate_line()
        self.color = None

    @abstractmethod
    def validate_line(self):
        """
        Validate the line and return a status code.

        This method should analyze the line content and determine its validity
        according to the specific rules for each line type (differs for each config file).

        Returns:
            int: Status code (VALID, INVALID, WARNING, COMMENT)
        """
        pass

    def set_status(self, status):
        """
        Set the validation status for this line.

        Args:
            status (int): Status code to assign to the line
        """
        self.status = status

    def set_color(self, color):
        """
        Set the display color for this line.

        The color is typically used for syntax highlighting or
        indicating validation status in the UI.

        Args:
            color: Color specification (implementation-dependent)
        """
        self.color = color

    def get_line(self):
        """
        Get the line as a string.

        Returns:
            str: The raw text content of the line
        """
        return self.line

    def get_status(self):
        """
        Get the validation status of this line.

        Returns:
            int: Status code (VALID, INVALID, WARNING, or COMMENT)
        """
        return self.status

    def get_color(self):
        """
        Get the display color of this line.

        Returns:
            object: Color specification (implementation-dependent)
        """
        return self.color