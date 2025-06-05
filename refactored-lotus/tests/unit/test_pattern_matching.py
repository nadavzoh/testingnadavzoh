"""Unit tests for pattern matching classes."""
import unittest
from unittest.mock import patch, MagicMock

from src.core.services.PatternMatcher import PatternMatcher
from src.core.services.PatternMatchingService import PatternMatchingService


class TestPatternMatcher(unittest.TestCase):
    """Test case for the PatternMatcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mocks for dependencies
        self.mock_files_manager = MagicMock()
        self.mock_fly_netlist = MagicMock()
        
        # Configure the mock fly_netlist with test data
        mock_top_cell = MagicMock()
        mock_top_cell.get_name.return_value = "top_cell"
        
        mock_template1 = MagicMock()
        mock_template1.get_name.return_value = "template1"
        
        mock_template2 = MagicMock()
        mock_template2.get_name.return_value = "template2"
        
        self.mock_fly_netlist.get_top_cell.return_value = mock_top_cell
        self.mock_fly_netlist.get_templates.return_value = [mock_template1, mock_template2]
        self.mock_fly_netlist.get_all_nets.side_effect = lambda t: {
            "top_cell": ["net1", "net2", "net[3]", "net[4]", "complex[1]net[5]"],
            "template1": ["net1", "net2", "net[3]", "other_net"],
            "template2": ["net1", "unique_net", "net[3]", "complex[2]net[6]"]
        }.get(t, [])
        
        self.mock_fly_netlist.read_spice_file.return_value = self.mock_fly_netlist
        
        # Create the pattern matcher with mocked dependencies
        self.pattern_matcher = PatternMatcher(self.mock_files_manager, self.mock_fly_netlist)
    
    def test_get_all_templates(self):
        """Test retrieving all templates."""
        templates = self.pattern_matcher.get_all_templates()
        self.assertEqual(templates, ["template1", "template2"])
    
    def test_get_all_nets(self):
        """Test retrieving all nets for a template."""
        nets = self.pattern_matcher.get_all_nets("template1")
        self.assertEqual(nets, ["net1", "net2", "net[3]", "other_net"])
    
    def test_expand_bus_notation(self):
        """Test expanding bus notation patterns."""
        # Simple bus notation
        expanded = PatternMatcher._expand_bus_notation("net[1:3]")
        self.assertEqual(expanded, ["net[1]", "net[2]", "net[3]"])
        
        # Multiple bus notations
        expanded = PatternMatcher._expand_bus_notation("complex[1:2]net[3:4]")
        expected = [
            "complex[1]net[3]",
            "complex[1]net[4]",
            "complex[2]net[3]",
            "complex[2]net[4]"
        ]
        self.assertEqual(sorted(expanded), sorted(expected))
        
        # No bus notation
        expanded = PatternMatcher._expand_bus_notation("regular_net")
        self.assertEqual(expanded, ["regular_net"])
    
    def test_find_matches_exact(self):
        """Test finding matches with exact matching."""
        matches, templates = self.pattern_matcher.find_matches("template1", "net1", False, False)
        
        self.assertEqual(templates, ["template1"])
        self.assertEqual(matches, ["template1:net1"])
    
    def test_find_matches_bus_notation(self):
        """Test finding matches with bus notation."""
        # Test simple bus notation
        matches, templates = self.pattern_matcher.find_matches("template1", "net[1:2]", False, False)
        expected_matches = ["template1:net[1]", "template1:net[2]"]
        self.assertEqual(sorted(matches), sorted(expected_matches))
        
        # Test multiple bus notations across templates
        matches, templates = self.pattern_matcher.find_matches(None, "complex[1:2]net[5:6]", False, False)
        expected_matches = ["top_cell:complex[1]net[5]", "template2:complex[2]net[6]"]
        self.assertEqual(sorted(matches), sorted(expected_matches))
    
    def test_find_matches_regex(self):
        """Test finding matches with regex."""
        # Test regex for net matching
        matches, templates = self.pattern_matcher.find_matches("template1", "net\\d", False, True)
        expected_matches = ["template1:net1", "template1:net2"]
        self.assertEqual(sorted(matches), sorted(expected_matches))
        
        # Test regex for template matching
        matches, templates = self.pattern_matcher.find_matches("template\\d", "unique_net", True, False)
        expected_matches = ["template2:unique_net"]
        self.assertEqual(matches, expected_matches)


class TestPatternMatchingService(unittest.TestCase):
    """Test case for the PatternMatchingService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_pattern_matcher = MagicMock()
        self.mock_pattern_matcher.find_matches.return_value = (
            ["template1:net1", "template2:net2"],  # matches
            ["template1", "template2"]            # templates
        )
        self.mock_pattern_matcher._expand_bus_notation.return_value = ["net[1]", "net[2]", "net[3]"]
        
        self.service = PatternMatchingService(self.mock_pattern_matcher)
    
    def test_find_matches(self):
        """Test finding matches through the service."""
        matches, templates = self.service.find_matches("template", "net", True, False)
        
        # Verify that the pattern matcher was called with the correct parameters
        self.mock_pattern_matcher.find_matches.assert_called_with("template", "net", True, False)
        
        # Check that the service returns the expected results
        self.assertEqual(matches, ["template1:net1", "template2:net2"])
        self.assertEqual(templates, ["template1", "template2"])
    
    def test_get_all_templates(self):
        """Test retrieving all templates through the service."""
        self.mock_pattern_matcher.get_all_templates.return_value = ["template1", "template2"]
        
        templates = self.service.get_all_templates()
        self.assertEqual(templates, ["template1", "template2"])
    
    def test_get_all_nets(self):
        """Test retrieving all nets for a template through the service."""
        self.mock_pattern_matcher.get_all_nets.return_value = ["net1", "net2"]
        
        nets = self.service.get_all_nets("template1")
        self.assertEqual(nets, ["net1", "net2"])
        self.mock_pattern_matcher.get_all_nets.assert_called_with("template1")
    
    def test_expand_bus_notation(self):
        """Test expanding bus notation through the service."""
        expanded = self.service.expand_bus_notation("net[1:3]")
        
        self.mock_pattern_matcher._expand_bus_notation.assert_called_with("net[1:3]")
        self.assertEqual(expanded, ["net[1]", "net[2]", "net[3]"])


if __name__ == '__main__':
    unittest.main()