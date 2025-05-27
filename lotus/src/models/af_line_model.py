from models.abstract_line_model import AbstractLineModel
from services.lotus_utils import parse_af_line
# TODO: move the logic of finding matches for each line to this class


class AfLineModel(AbstractLineModel):
    """
    Model for Activity Factor configuration lines.

    This class represents a single line in an Activity Factor configuration file,
    providing methods to parse, validate, and access its various properties.
    It inherits from AbstractLineModel to allow for polymorphic line handling.

    Attributes:
        line (str): The raw text of the line
        net_matches (list): List of matched nets
        template_matches (list): List of matched templates
        template (str): Template pattern from the line
        template_regex (bool): Whether template uses regex matching
        net (str): Net pattern from the line
        net_regex (bool): Whether net uses regex matching
        activity_factor (str): Activity factor value
        em_enabled (bool): Whether EM analysis is enabled
        sh_enabled (bool): Whether SH analysis is enabled
    """

    def __init__(self, line: str, net_matches=None, template_matches=None):
        """
        Initialize an AF line model with the raw line text and optional matches.

        Args:
            line (str): The raw text of the line
            net_matches (list, optional): List of net matches. Defaults to None.
            template_matches (list, optional): List of template matches. Defaults to None.
        """
        super().__init__(line)

        self.net_matches = net_matches if net_matches is not None else []
        self.template_matches = template_matches if template_matches is not None else []
        self.template = None
        self.template_regex = False
        self.net = None
        self.net_regex = False
        self.activity_factor = None
        self.em_enabled = False
        self.sh_enabled = False
        # Parse the line fields if it's not a comment or an empty line
        if not line.startswith('#') and line.strip():
            fields = self.get_fields_dict()
            if fields:
                self.template = fields.get('template')
                self.template_regex = fields.get('template_regex', False)
                self.net = fields.get('net')
                self.net_regex = fields.get('net_regex', False)
                self.activity_factor = fields.get('af')
                self.em_enabled = fields.get('em', False)
                self.sh_enabled = fields.get('sh', False)

    def validate_line(self):
        """
        Validate the line based on its content.

        Checks if the line is empty, a comment, or has the required
        number of fields for a valid Activity Factor configuration.

        Returns:
            int: Validation status (VALID, INVALID, COMMENT)
        """
        if not self.line.strip():
            return self.VALID

        if self.line.startswith('#'):
            return self.COMMENT

        # Basic validation for AF tab: line should have at least 3 fields, TODO: agree on a better format
        fields = self.line.split()
        if len(fields) < 3 or len(fields) > 3 or fields[2].startswith("regexp_sch"):  # tmp fix
            return self.INVALID

        return self.VALID

    def get_fields_dict(self):
        """
        Parse an AF configuration line into structured fields.

        Extracts template, net, activity factor, and flags from the line text,
        handling different possible line formats.

        Returns:
            dict: Dictionary with parsed fields or None if parsing failed
        """
        return parse_af_line(self.line)

    def set_net_matches(self, matches):
        """
        Set the net matches for this line.

        Args:
            matches (list): List of net matches
        """
        self.net_matches = matches

    def set_template_matches(self, matches):
        """
        Set the template matches for this line.

        Args:
            matches (list): List of template matches
        """
        self.template_matches = matches

    def get_template(self):
        """
        Get the template for this line.

        Returns:
            str: Template string or None if not present
        """
        return self.template

    def get_template_regex(self):
        """
        Check if template regex is enabled for this line.

        Returns:
            bool: True if template regex is enabled, False otherwise
        """
        return self.template_regex

    def get_net(self):
        """
        Get the net for this line.

        Returns:
            str: Net string or None if not present
        """
        return self.net

    def get_net_regex(self):
        """
        Check if net regex is enabled for this line.

        Returns:
            bool: True if net regex is enabled, False otherwise
        """
        return self.net_regex

    def get_activity_factor(self):
        """
        Get the activity factor for this line.

        Returns:
            str: Activity factor string or None if not present
        """
        return self.activity_factor

    def get_em_enabled(self):
        """
        Check if EM analysis is enabled for this line.

        Returns:
            bool: True if EM analysis is enabled, False otherwise
        """
        return self.em_enabled

    def get_sh_enabled(self):
        """
        Check if SH analysis is enabled for this line.

        Returns:
            bool: True if SH analysis is enabled, False otherwise
        """
        return self.sh_enabled

    def get_net_matches(self):
        """
        Get the net matches for this line.

        Returns:
            list: List of net matches
        """
        return self.net_matches

    def get_template_matches(self):
        """
        Get the template matches for this line.

        Returns:
            list: List of template matches
        """
        return self.template_matches

    def __repr__(self):
        """
        String representation of the AfLineModel.

        Returns:
            str: String representation of the model for debugging
        """
        return f"AfLineModel(line={self.line})"

    def __str__(self):
        """
        String representation of the AfLineModel.

        Returns:
            str: The raw line text
        """
        return self.line
