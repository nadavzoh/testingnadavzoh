import re
from functools import lru_cache  # caching
from fly.fly_netlist import FlyNetlistBuilder
from managers.lotus_file_manager import LotusFileManager
from services.lotus_utils import parse_af_line

class PatternMatcher:
    """
    Singleton class to manage pattern matching in Lotus' AF Tab.

    This class provides tools for parsing configuration lines and matching
    template/net patterns against the loaded spice netlist. It implements
    the Singleton pattern to ensure only one instance exists across the application,
    as it loads potentially large netlist data.

    Attributes:
        _instance: Class variable for Singleton pattern
        _initialized (bool): Flag indicating if instance has been initialized
        _files_manager: Instance of LotusFileManager for accessing files
        _fly_netlist: The loaded spice netlist data
        top_cell (str): Name of the top cell in the netlist
        all_templates (list): List of all template names in the netlist
        all_nets_in_templates (dict): Dictionary mapping template names to their nets
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Override __new__ to implement the Singleton pattern.

        Returns:
            PatternMatcher: The singleton instance of this class
        """
        if cls._instance is None:
            cls._instance = super(PatternMatcher, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initialize the PatternMatcher.

        Loads the spice file and builds netlist data structures for pattern matching.
        Only runs initialization once due to Singleton pattern.

        Raises:
            FileNotFoundError: If the spice file cannot be found
            Exception: If any other error occurs during initialization
        """
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._files_manager = LotusFileManager()

            try:
                self._fly_netlist = FlyNetlistBuilder.read_spice_file(
                    self._files_manager.get_fub(), self._files_manager.get_spice_file())
            except FileNotFoundError as e:
                print(f"Spice file not found: {self._files_manager.get_spice_file()} {e}")
                raise FileNotFoundError(f"Spice file not found: {self._files_manager.get_spice_file()}")
            except Exception as e:
                print(f"Error loading netlist: {e}")
                raise

            self.top_cell = self._fly_netlist.get_top_cell().get_name()
            self.all_templates = [t.get_name() for t in self._fly_netlist.get_templates()]
            self.all_nets_in_templates = {t: self._fly_netlist.get_all_nets(t) for t in self.all_templates}

    def parse_line(self, line):
        """
        Parse a configuration line into structured fields.

        Extracts template, net, AF value and flags from a configuration line.

        Args:
            line (str): The line text to parse

        Returns:
            dict: Dictionary with parsed fields or None if parsing failed

        Fields in returned dictionary:
            - template: Template name or None if not specified
            - net: Net name
            - af: AF value
            - template_regex: Boolean indicating if template is a regex pattern
            - net_regex: Boolean indicating if net is a regex pattern
            - em: Boolean indicating if EM flag is set
            - sh: Boolean indicating if SH flag is set
        """
        return parse_af_line(line)

    @lru_cache(maxsize=256)
    def find_matches(self, template_name, net_name, template_regex, net_regex):
        """
        Find matches for a template and net pattern in the netlist.

        Uses regular expressions if specified to match templates and nets.
        Results are cached using lru_cache for performance.

        Args:
            template_name (str): Name or pattern of the template to match
            net_name (str): Name or pattern of the net to match
            template_regex (bool): Whether template_name should be treated as a regex pattern
            net_regex (bool): Whether net_name should be treated as a regex pattern

        Returns:
            tuple: (net_matches, template_matches) where:
                - net_matches (list): List of matching nets in "template:net" format
                - template_matches (list): List of matching template names
        """
        if not template_name and not net_name:
            return [], []

        top_cell = self.top_cell
        # Default to top cell if no template is specified
        template_name = template_name or top_cell

        # Compile regex patterns with proper error handling
        template_pattern = None
        net_pattern = None

        if template_regex and template_name:
            try:
                template_pattern = re.compile(template_name)
            except re.error as e:
                print(f"Invalid template regex pattern '{template_name}': {e}")
                return [], []

        if net_regex and net_name:
            try:
                net_pattern = re.compile(net_name)
            except re.error as e:
                print(f"Invalid net regex pattern '{net_name}': {e}")
                return [], []

        # Get matching templates
        if template_regex:
            all_template_names = self.all_templates
            if template_name == top_cell:  # user didn't specify a template name
                all_template_names = [top_cell]
            try:
                matching_templates = [t for t in all_template_names if template_pattern.search(t)]
            except Exception as e:
                print(f"Error matching template pattern '{template_name}': {e}")
                return [], []

            if not matching_templates:
                return [], []
        else:
            matching_templates = [template_name] if template_name in self.all_templates else []

        matching_nets = []
        for template in matching_templates:
            all_nets = self.all_nets_in_templates.get(template, [])
            if not all_nets:
                continue

            # Get matching nets
            for net in all_nets:
                try:
                    if net_regex:
                        match = net_pattern and net_pattern.search(net)
                    else:
                        match = net_name == net

                    if match:
                        matching_nets.append(f'{template}:{net}')
                except Exception as e:
                    print(f"Error matching net pattern '{net_name}' against '{net}': {e}")
                    continue

        return matching_nets, matching_templates

    def get_all_templates(self):
        """
        Get all available templates in the netlist.

        Returns:
            list: List of all template names in the loaded netlist
        """
        return self.all_templates

    def get_all_nets(self, template):
        """
        Get all nets in a specific template.

        Args:
            template (str): Name of the template to retrieve nets for

        Returns:
            list: List of net names in the template or empty list if template not found
        """
        return self.all_nets_in_templates.get(template, [])