from typing import List, Tuple, Optional
from src.core.services.PatternMatcher import PatternMatcher

class PatternMatchingService:
    """
    Service for pattern matching operations.
    
    This service wraps the PatternMatcher class and provides a higher-level API
    for pattern matching operations. It's designed to be used by presenters and
    other services that need to find matches for templates and nets.

    """
    
    def __init__(self, pattern_matcher: PatternMatcher):
        """
        Initialize the service with a PatternMatcher instance.
        
        Args:
            pattern_matcher: The PatternMatcher instance to use
        """
        self._pattern_matcher = pattern_matcher
    
    def find_matches(self, template_name: Optional[str], net_name: str,
                    template_regex: bool, net_regex: bool) -> Tuple[List[str], List[str]]:
        """
        Find template and net matches based on the provided patterns and regex flags.
        
        Args:
            template_name (Optional[str]): Name or pattern of the template to match, can be None
            net_name (str): Name or pattern of the net to match, required
            template_regex (bool): Whether template_name should be treated as a regex pattern
            net_regex (bool): Whether net_name should be treated as a regex pattern
            
        Returns:
            tuple: (net_matches, template_matches)
        """
        return self._pattern_matcher.find_matches(template_name, net_name, template_regex, net_regex)
    
    def get_all_templates(self) -> List[str]:
        """
        Get all templates from the pattern matcher.
        
        Returns:
            list: List of all template names
        """
        return self._pattern_matcher.get_all_templates()
    
    def get_all_nets(self, template: str) -> List[str]:
        """
        Get all nets for a template from the pattern matcher.
        
        Args:
            template (str): Name of the template to retrieve nets for
            
        Returns:
            list: List of net names in the template
        """
        return self._pattern_matcher.get_all_nets(template)
    
    def expand_bus_notation(self, pattern: str) -> List[str]:
        """
        Expand a bus notation pattern into all possible concrete names.
        
        Args:
            pattern (str): The pattern with bus notation [start:end]
            
        Returns:
            list: All expanded concrete names
        """
        return PatternMatcher._expand_bus_notation(pattern)