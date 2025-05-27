from services.pattern_matcher import PatternMatcher
from models.abstract_dialog_model import AbstractDialogModel
from services.lotus_utils import parse_af_line
import re


class AfDialogModel(AbstractDialogModel):
    """
    Model for Activity Factor configuration dialog.

    This model provides the data and logic for the Activity Factor dialog,
    handling the parsing, validation, and formatting of AF configuration lines.

    Attributes:
        matcher (PatternMatcher): Instance for finding matching nets and templates
        net (str): Current net pattern string
        net_regex (bool): Whether net is a regex pattern
        template (str): Current template pattern string
        template_regex (bool): Whether template is a regex pattern
        activity_factor (str): Activity factor value (0-1)
        float_regex_pattern (Pattern): Regex for validating activity factor
        em_enabled (bool): Whether EM mode is enabled
        sh_enabled (bool): Whether SH mode is enabled
        current_line (str): The current formatted line
    """

    def __init__(self):
        """Initialize the model with default values."""
        self.matcher = PatternMatcher()
        self.net = ""
        self.net_regex = False
        self.template = ""
        self.template_regex = False

        self.activity_factor = ""
        # Regex for validating activity factor as a float between 0 and 1
        self.float_regex_pattern = re.compile(r"^0(\.\d+)?|1(\.0+)?$")

        self.em_enabled = False
        self.sh_enabled = False

        self.current_line = ""

    def find_matches(self):
        """
        Find pattern matches for the current template and net.

        Uses the PatternMatcher service to find matches for the current
        template and net patterns in the netlist.

        Returns:
            tuple: (net_matches, template_matches) where:
                - net_matches is a list of matching net strings
                - template_matches is a list of matching template names
        """
        if not self.net:
            return [], []

        return self.matcher.find_matches(
            self.template,
            self.net,
            self.template_regex,
            self.net_regex
        )

    def format_line(self):
        """
        Format the model data as a line for the configuration file.

        Creates a properly formatted configuration line from the current model data,
        including pattern, activity factor, and flags.

        Returns:
            str: Formatted line ready to be inserted into the configuration file
        """
        if self.template:
            if self.net:
                pattern = f"{{{self.template}:{self.net}}}"
            else:
                pattern = f"{{{self.template}}}"
        else:
            pattern = f"{{{self.net}}}"

        parts = [pattern]

        if self.activity_factor:
            parts.append(self.activity_factor)

        flags = []
        if self.template:
            if self.template_regex:
                flags.append("template-regexp")
            else:
                flags.append("template-regular")
        if self.net:
            if self.net_regex:
                flags.append("net-regexp")
            else:
                flags.append("net-regular")

        if self.em_enabled or self.sh_enabled:
            flags.append("sch")
        if self.em_enabled:
            flags.append("em")
        if self.sh_enabled:
            flags.append("sh")

        pattern_and_af_str = " ".join(parts)
        flags_str = "_".join(flags)

        line = pattern_and_af_str + " " + flags_str
        self.current_line = line
        return line

    def get_fields_from_line(self, line):
        """
        Parse a configuration line into structured fields.

        Extracts pattern, activity factor, and flags from a line in the configuration file.

        Args:
            line (str): The line to parse

        Returns:
            dict: Dictionary with the parsed fields:

                - template: str, Template name or empty string
                - net: str, Net pattern
                - af: str, Activity factor value
                - template_regex: bool, Whether template is a regex
                - net_regex: bool, Whether net is a regex
                - em: bool, Whether EM is enabled
                - sh: bool, Whether SH is enabled
        Raises:
            ValueError: If the line format is invalid
        """
        if not line:
            return {}
            
        self.current_line = line
        
        parsed_fields = parse_af_line(line)
        
        if not parsed_fields:
            raise ValueError("Invalid line format")

        if parsed_fields['template'] is None:
            parsed_fields['template'] = ""
            
        return parsed_fields

    def validate_input(self):
        """
        Validate the current input data.

        Ensures that all required fields are populated and valid.

        Returns:
            bool: True if all inputs are valid

        Raises:
            ValueError: With descriptive message if validation fails
        """
        if not self.net:
            raise ValueError("Pattern is required")

        if not self.activity_factor:
            raise ValueError("Activity Factor is required")

        if not self.float_regex_pattern.match(self.activity_factor):
            raise ValueError("Activity Factor must be a number between 0 and 1")

        return True