import re
from functools import lru_cache
from fly.fly_netlist import FlyNetlistBuilder

class PatternMatcher:
    def __init__(self):
        self._fly_netlist = FlyNetlistBuilder.read_spice_file(
            'dcchunkrotd', 'some_spice_file.sp')
        self.find_matches = self._cached_find_matches()

    def _cached_find_matches(self):
        """
        Creates a cached version of find_matches with a custom cache key
        that handles the complex input types
        """

        @lru_cache(maxsize=128)
        def cached_find_matches(template_name: str, net_name: str,
                                template_regex: bool, net_regex: bool):
            print("Cache miss")
            if not template_name and not net_name:
                return (), ()
            top_cell = self._fly_netlist.get_top_cell().get_name()
            # Default to top cell if no template is specified
            template_name = template_name or top_cell
            try:
                template_pattern = re.compile(template_name) if template_regex else None
                net_pattern = re.compile(net_name) if net_regex else None
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
            # Get matching templates
            if template_regex:
                all_template_names = [t.get_name() for t in self._fly_netlist.get_templates()]
                if template_name == top_cell:  # user didn't specify a template name
                    all_template_names = [top_cell]
                matching_templates = [t for t in all_template_names if template_pattern.search(t)]
                if not matching_templates:
                    return (), ()
            else:
                matching_templates = [template_name]

            matching_nets = []
            for template in matching_templates:
                all_nets = self._fly_netlist.get_all_nets(template)
                # Get matching nets
                for net in all_nets:
                    match = (
                            (not net_regex and net_name == net) or
                            (net_regex and net_pattern.search(net))
                    )
                    if match:
                        matching_nets.append(f'{template}:{net}')
            # Convert to tuple for hashability with lru_cache
            return tuple(matching_nets), tuple(matching_templates)

        return cached_find_matches