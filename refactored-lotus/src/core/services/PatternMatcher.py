import re
from functools import lru_cache  # caching
from fly.fly_netlist import FlyNetlistBuilder
from src.core.services.ConfigService import ConfigService
from typing import List, Tuple, Optional, Pattern, Callable

class PatternMatcher:
    """
    Service class to manage pattern matching in Lotus' AF Tab.

    This class provides tools for parsing configuration lines and matching
    template/net patterns against the loaded spice netlist. It's designed to be
    registered with a service locator for global access.

    Attributes:
        _files_manager: Instance of ConfigService
        _fly_netlist: The loaded spice netlist data
        top_cell (str): Name of the top cell in the netlist
        all_templates (list): List of all template names in the netlist
        all_nets_in_templates (dict): Dictionary mapping template names to their nets
    """

    def __init__(self, config_service: ConfigService, fly_netlist: FlyNetlistBuilder):
        """
        Initialize the PatternMatcher.

        Loads the spice file and builds netlist data structures for pattern matching.

        Args:
            config_service: Service for accessing files
            fly_netlist: Builder for working with netlist data

        Raises:
            FileNotFoundError: If the spice file cannot be found
            Exception: If any other error occurs during initialization
        """
        self._config_service = config_service
        try:
            print(self._config_service.get_config("fub"))
            print(self._config_service.get_config("spice_file"))
            self._fly_netlist = fly_netlist.read_spice_file(
                self._config_service.get_config("fub"), self._config_service.get_file_path("spice_file"))
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Spice file not found: {e.filename}. Please check the configuration.")
        except Exception as e:
            raise Exception(f"Error loading netlist: {e}")            

        self.top_cell = self._fly_netlist.get_top_cell().get_name()
        self.all_templates = [t.get_name() for t in self._fly_netlist.get_templates()]
        self.all_nets_in_templates = {t: self._fly_netlist.get_all_nets(t) for t in self.all_templates}

    def get_all_templates(self) -> List[str]:
        """
        Get all available templates in the netlist.

        Returns:
            list: List of all template names in the loaded netlist
        """
        return self.all_templates

    def get_all_nets(self, template) -> List[str]:
        """
        Get all nets in a specific template.

        Args:
            template (str): Name of the template to retrieve nets for

        Returns:
            list: List of net names in the template or empty list if template not found
        """
        return self.all_nets_in_templates.get(template, [])

    @staticmethod
    def _expand_bus_notation(pattern: str) -> List[str]:
        """
        Expand a bus notation pattern into a list of all possible concrete names.
                
        Examples:
            "mynet[1:3]" -> ["mynet[1]", "mynet[2]", "mynet[3]"]
            "my[1:2]net[3:4]" -> ["my[1]net[3]", "my[1]net[4]", "my[2]net[3]", "my[2]net[4]"]
        
        Args:
            pattern (str): The pattern with bus notation [start:end]
            
        Returns:
            list: All expanded concrete names
        """
        if not pattern or '[' not in pattern or ']' not in pattern:
            return [pattern]
            
        # Look for [num:num] pattern
        bus_pattern = re.compile(r'\[(\d+):(\d+)\]')
        match = bus_pattern.search(pattern)
        
        if not match:
            return [pattern]
            
        start, end = int(match.group(1)), int(match.group(2))
        if start > end:
            start, end = end, start
            
        # Replace the first bus notation with each value in the range
        result = []
        prefix = pattern[:match.start()]
        suffix = pattern[match.end():]
        
        for i in range(start, end + 1):
            # Recursively expand any remaining bus notations
            expanded = PatternMatcher._expand_bus_notation(f"{prefix}[{i}]{suffix}")
            result.extend(expanded)
            
        return result

    @lru_cache(maxsize=256)
    def find_matches(self, template_name: Optional[str], net_name: str,
                     template_regex: bool, net_regex: bool) -> Tuple[List[str], List[str]]:
        """
        Find matches for a template and net pattern in the netlist.

        Uses regular expressions if specified to match templates and nets.
        Supports bus notation (e.g., net[1-3]) when regex is disabled.
        Results are cached using lru_cache for performance.

        Args:
            template_name (Optional[str]): Name or pattern of the template to match, can be None
            net_name (str): Name or pattern of the net to match, required
            template_regex (bool): Whether template_name should be treated as a regex pattern
            net_regex (bool): Whether net_name should be treated as a regex pattern

        Returns:
            tuple: (net_matches, template_matches) where:
                - net_matches (list): List of matching nets in "template:net" format
                - template_matches (list): List of matching template names
        """
        if not template_name and not net_name:
            return [], []

        # Set default template name
        template_name = template_name or self.top_cell

        # Get matching templates
        matching_templates = self._get_matching_templates(template_name, template_regex)
        if not matching_templates:
            return [], []

        # Get matching nets for all templates
        matching_nets = self._get_matching_nets(matching_templates, net_name, net_regex)

        return matching_nets, matching_templates

    def _get_matching_templates(self, template_name: str, template_regex: bool) -> List[str]:
        """
        Get list of templates that match the given pattern.
        """
        if not template_regex:
            return [template_name] if template_name in self.all_templates else []

        # Handle regex matching
        template_pattern = self._compile_regex_pattern(template_name, "template")
        if not template_pattern:
            return []

        # Determine search scope
        search_templates = ([self.top_cell] if template_name == self.top_cell 
                        else self.all_templates)

        try:
            return [t for t in search_templates if template_pattern.search(t)]
        except Exception as e:
            print(f"Error matching template pattern '{template_name}': {e}")
            return []

    def _get_matching_nets(self, templates: List[str], net_name: str, net_regex: bool) -> List[str]:
        """
        Get all matching nets across the given templates.
        """
        if not net_name:
            return []

        # Determine net matching strategy
        net_matcher = self._create_net_matcher(net_name, net_regex)
        
        matching_nets = []
        for template in templates:
            template_nets = self.all_nets_in_templates.get(template, [])
            if template_nets:
                matching_nets.extend(net_matcher(template, template_nets))

        return matching_nets

    def _create_net_matcher(self, net_name: str, net_regex: bool) -> Callable[[str, List[str]], List[str]]:
        """
        Create and return appropriate net matching function.
        """
        if net_regex:
            return self._create_regex_net_matcher(net_name)
        elif self._has_bus_notation(net_name):
            return self._create_bus_net_matcher(net_name)
        else:
            return self._create_exact_net_matcher(net_name)

    def _create_regex_net_matcher(self, net_name: str) -> Callable[[str, List[str]], List[str]]:
        """
        Create regex-based net matcher.
        """
        net_pattern = self._compile_regex_pattern(net_name, "net")
        if not net_pattern:
            return lambda template, nets: []

        def regex_matcher(template, nets):
            matches = []
            for net in nets:
                try:
                    if net_pattern.search(net):
                        matches.append(f'{template}:{net}')
                except Exception as e:
                    print(f"Error matching net pattern '{net_name}' against '{net}': {e}")
            return matches
        
        return regex_matcher

    def _create_bus_net_matcher(self, net_name: str) -> Callable[[str, List[str]], List[str]]:
        """
        Create bus notation-based net matcher.
        """
        expanded_patterns = PatternMatcher._expand_bus_notation(net_name)
        expanded_set = set(expanded_patterns)  # Use set for O(1) lookup
        
        def bus_matcher(template, nets):
            return [f'{template}:{net}' for net in nets if net in expanded_set]
        
        return bus_matcher

    def _create_exact_net_matcher(self, net_name: str) -> Callable[[str, List[str]], List[str]]:
        """
        Create exact string matching net matcher.
        """
        def exact_matcher(template, nets):
            return [f'{template}:{net}' for net in nets if net == net_name]
        
        return exact_matcher

    @staticmethod
    def _compile_regex_pattern(pattern: str, pattern_type: str) -> Optional[Pattern]:
        """
        Compile regex pattern with error handling.
        """
        try:
            return re.compile(pattern)
        except re.error as e:
            print(f"Invalid {pattern_type} regex pattern '{pattern}': {e}")
            return None

    @staticmethod
    def _has_bus_notation(net_name: str) -> bool:
        """
        Check if net name contains bus notation.
        """
        return '[' in net_name and ']' in net_name