import re
from typing import List, Optional, Dict, Any, Tuple
from src.core.models.LineModelInterface import LineModelInterface
from src.core.services.ServiceLocator import ServiceLocator

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
    AF_LINE_REGEX = re.compile(
    r'^\s*\{\s*(?:(?P<template>[^:}]+)\s*:\s*)?'
    r'(?P<net>[^}]+)\s*\}\s*'
    r'(?P<af_value>[0-9]*\.?[0-9]+)\s*'
    r'(?:(?P<regex>(?:template-(?:regexp|regular)_net-(?:regexp|regular))|'
    r'(?:net-(?:regexp|regular)_template-(?:regexp|regular)))_'
    r'(?P<mode>sch_em(?:_sh)?|sch_sh))?\s*$'
    )
    
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
        self._matches = {'templates': [], 'nets': []}
        self._status = self.UN_INITIALIZED

        # Parse the line to extract components
        self._parse_line()
        # Only find matches if the model is valid and we can get the pattern matching service
        if (not self.is_comment() and 
            self.get_status() != self.INVALID and
            self.get_net() and  # Net is required for matching
            ServiceLocator.is_registered('pattern_matching_service')):
            
            self.pattern_matching_service = ServiceLocator.get('pattern_matching_service')
            
            matches = self.pattern_matching_service.find_matches(
                self.get_template(),
                self.get_net(),
                self.is_template_regex(),
                self.is_net_regex()
            )
            self.set_matches(matches)
        
        # Validate the line after parsing
        self._status = self.validate()


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
        self._parse_line()
        # Re-validate the line after setting new content
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
        
        if len(self._matches['nets']) == 0:
            return self.WARNING
        
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
        Parse the line content to extract components using the static AF_LINE_REGEX pattern.
        Extracts template, net, AF value, and flags from the line content.
        """
        if self.is_comment() or not self._content.strip():
            return
            
        match = self.AF_LINE_REGEX.match(self._content)
        if match:
            # Extract the groups from the regex match
            groups = match.groupdict()
            
            # Template is optional, so check if it exists
            self._template = groups.get('template', '').strip() if groups.get('template') else ''
            self._net = groups.get('net', '').strip()
            self._af_value = groups.get('af_value', '').strip()
            
            # Extract regex and mode information if present
            regex_info = groups.get('regex', '') if groups.get('regex') else ''
            mode_info = groups.get('mode', '') if groups.get('mode') else ''
            # Parse flags from regex and mode information if available
            if regex_info:
                self._is_template_regex = 'template-regexp' in regex_info
                self._is_net_regex = 'net-regexp' in regex_info
            else:
                # Default to no regex if not specified
                self._is_template_regex = False
                self._is_net_regex = False
            
            if mode_info:
                self._is_em_enabled = 'em' in mode_info
                self._is_sh_enabled = 'sh' in mode_info
            else:
                # Default to both EM and SH being enabled if no mode is specified
                self._is_em_enabled = True
                self._is_sh_enabled = True

    
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
    
    def get_matches(self) -> Dict[str, List[str]]:
        """
        Get a deep copy of a dictionary of matches for templates and nets.
        
        Returns:
            Dict[str, List[str]]: A dictionary containing two lists:
            - 'templates': List of template matches
            - 'nets': List of net matches
        """
        return {
            'templates': self._matches['templates'][:],
            'nets': self._matches['nets'][:]
        }

    def set_matches(self, matches: Tuple[List[str], List[str]]) -> None:
        """
        Set the matches for this line.
        
        This is typically called by the factory after using a pattern matcher service
        to find matches for the template and net patterns.
        
        Args:
            matches (Tuple[List[str], List[str]]): A tuple containing two lists:
                - List of net matches
                - List of template matches
        """
        self._matches = {
            'nets': matches[0],
            'templates': matches[1]
        }
        # Re-validate the line after setting matches
        self._status = self.validate()


    # def get_hint(self) -> str:
    #     """
    #     Get a hint for this line (e.g., error message).
        
    #     Returns:
    #         str: A hint or error message
    #     """
    #     if self._status == self.COMMENT:
    #         return "Comment line"
    #     elif self._status == self.WARNING:
    #         return "Empty line"
    #     elif self._status == self.INVALID:
    #         if not re.match(self.AF_LINE_REGEX, self._content):
    #             return "Invalid AF line format. Expected format: {template:net} AF_VALUE [flags]"
    #         try:
    #             af_value = float(self._af_value)
    #             if not (0 <= af_value <= 1):
    #                 return "Invalid AF value. Must be between 0 and 1."
    #         except ValueError:
    #             return "Invalid AF value. Must be a number between 0 and 1."
    #     return ""
