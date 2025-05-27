import re
from typing import List, Optional, Dict, Any, Tuple

from src.core.models.LineModelInterface import LineModelInterface

# TODO: support bus notation
class AfLineModel(LineModelInterface):
    """
    Line model for Activity Factor (AF) configuration lines.
    
    This class implements the LineModelInterface for AF configuration lines,
    which have the format: `{template:net} AF_VALUE [flags]`.
    
    Attributes:
        content (str): The content of the line
        status (int): The validation status of the line
        template (str): The template pattern
        net (str): The net pattern
        af_value (str): The activity factor value
        is_template_regex (bool): Whether the template is a regex pattern
        is_net_regex (bool): Whether the net is a regex pattern
        is_em_enabled (bool): Whether EM mode is enabled
        is_sh_enabled (bool): Whether SH mode is enabled
    """
    
    # Regular expression for AF line format
    AF_LINE_REGEX = r'^\s*\{\s*([^:]+)\s*:\s*([^}]+)\s*\}\s*([0-9]*\.?[0-9]+)\s*(.*)$'
    
    def __init__(self, line_content: str):
        """
        Initialize the line model with the given content.
        
        Args:
            line_content: The content of the line
        """
        self._content = line_content
        self._template = ""
        self._net = ""
        self._af_value = ""
        self._is_template_regex = False
        self._is_net_regex = False
        self._is_em_enabled = False
        self._is_sh_enabled = False
        self._matches = []
        
        # Parse the line to extract components
        self._parse_line()
        self._status = self.validate()

        # TODO:
        # self._matches = []  # This should be populated by a pattern matcher service later.

    def get_content(self) -> str:
        """
        Get the line content.
        
        Returns:
            str: The content of the line
        """
        return self._content
    
    def set_content(self, content: str) -> None:
        """
        Set the line content.
        
        Args:
            content: The new content for the line
        """
        self._content = content
        self._parse_line()  # TODO: this will later be moved to a utility function, because finding matches needs it too.
        # or maybe not because when we load the file and create the line models we already parsed it and now we can just
        # send the data that was already parsed and not the whole line content.
        self._status = self.validate()
    
    def get_status(self) -> int:
        """
        Get the validation status of the line.
        
        Returns:
            int: The validation status (VALID, INVALID, WARNING, or COMMENT)
        """
        return self._status
    
    def validate(self) -> int:
        """
        Validate the line content.
        
        AF lines are valid if they match the expected format and have a valid AF value.
        
        Returns:
            int: The validation status (VALID, INVALID, WARNING, or COMMENT)
        """
        if self.is_comment():
            return self.COMMENT
        
        if len(self._matches) == 0:
            return self.WARNING
        
        # Check if the line matches the AF format
        if not re.match(self.AF_LINE_REGEX, self._content):
            return self.INVALID
        
        # Check if AF value is between 0 and 1
        try:
            af_value = float(self._af_value)
            if not (0 <= af_value <= 1):
                return self.INVALID
        except ValueError:
            return self.INVALID
        
        return self.VALID
    
    def is_comment(self) -> bool:
        """
        Check if the line is a comment.
        
        Returns:
            bool: True if the line is a comment, False otherwise
        """
        return self._content.strip().startswith('#')
    
    def _parse_line(self) -> None:
        """
        Parse the line content to extract components.
        """
        if self.is_comment() or not self._content.strip():
            return
        # TODO: template is optional so the regex and this method
        # must be adjusted to handle cases where the template is not provided.
        match = re.match(self.AF_LINE_REGEX, self._content)
        if match:
            self._template = match.group(1).strip()
            self._net = match.group(2).strip()
            self._af_value = match.group(3).strip()
            flags = match.group(4).strip().split()
            
            # Check for flags
            self._is_template_regex = "template-regexp" in flags
            self._is_net_regex = "net-regexp" in flags
            self._is_em_enabled = "_em" in flags
            self._is_sh_enabled = "_sh" in flags
    
    def get_template(self) -> str:
        """
        Get the template pattern.
        
        Returns:
            str: The template pattern
        """
        return self._template
    
    def get_net(self) -> str:
        """
        Get the net pattern.
        
        Returns:
            str: The net pattern
        """
        return self._net
    
    def get_af_value(self) -> str:
        """
        Get the activity factor value.
        
        Returns:
            str: The activity factor value
        """
        return self._af_value
    
    def is_template_regex(self) -> bool:
        """
        Check if the template is a regex pattern.
        
        Returns:
            bool: True if the template is a regex pattern, False otherwise
        """
        return self._is_template_regex
    
    def is_net_regex(self) -> bool:
        """
        Check if the net is a regex pattern.
        
        Returns:
            bool: True if the net is a regex pattern, False otherwise
        """
        return self._is_net_regex
    
    def is_em_enabled(self) -> bool:
        """
        Check if EM mode is enabled.
        
        Returns:
            bool: True if EM mode is enabled, False otherwise
        """
        return self._is_em_enabled
    
    def is_sh_enabled(self) -> bool:
        """
        Check if SH mode is enabled.
        
        Returns:
            bool: True if SH mode is enabled, False otherwise
        """
        return self._is_sh_enabled
    
    def get_matches(self) -> List[str]:
        """
        Get a list of matches for this line.
        
        Note: In a real implementation, this would query a pattern matcher service
        to find matching nets or templates. For now, we return a placeholder list.
        
        Returns:
            List[str]: A list of match strings
        """
        return self._matches
    
    def set_matches(self, matches: List[str]) -> None:
        """
        Set the matches for this line.
        
        This is typically called by a pattern matcher service after
        finding matches for the template and net patterns.
        
        Args:
            matches: The list of matches
        """
        self._matches = matches
    
    def get_hint(self) -> str:
        """
        Get a hint for this line (e.g., error message).
        
        Returns:
            str: A hint or error message
        """
        if self._status == self.COMMENT:
            return "Comment line"
        elif self._status == self.WARNING:
            return "Empty line"
        elif self._status == self.INVALID:
            if not re.match(self.AF_LINE_REGEX, self._content):
                return "Invalid AF line format. Expected format: {template:net} AF_VALUE [flags]"
            try:
                af_value = float(self._af_value)
                if not (0 <= af_value <= 1):
                    return "Invalid AF value. Must be between 0 and 1."
            except ValueError:
                return "Invalid AF value. Must be a number between 0 and 1."
        return ""
