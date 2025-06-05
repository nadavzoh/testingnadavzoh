"""Unit tests for line model classes."""
import unittest
from unittest.mock import patch, MagicMock

from src.core.models.BasicLineModel import BasicLineModel
from src.core.models.AfLineModel import AfLineModel
from src.core.models.LineModelInterface import LineModelInterface


class TestBasicLineModel(unittest.TestCase):
    """Test case for the BasicLineModel class."""
    
    def test_initialization(self):
        """Test initialization of a BasicLineModel."""
        model = BasicLineModel("Test line")
        self.assertEqual(model.get_content(), "Test line")
        
    def test_validation(self):
        """Test line validation."""
        # Test normal line
        model = BasicLineModel("Normal line")
        self.assertEqual(model.get_status(), LineModelInterface.VALID)
        
        # Test comment line
        model = BasicLineModel("# Comment line")
        self.assertEqual(model.get_status(), LineModelInterface.COMMENT)
        
        # Test empty line
        model = BasicLineModel("")
        self.assertEqual(model.get_status(), LineModelInterface.WARNING)


class TestAfLineModel(unittest.TestCase):
    """Test case for the AfLineModel class."""
    
    def test_initialization(self):
        """Test initialization of an AfLineModel."""
        # Valid AF line
        model = AfLineModel("{template:net} 0.5 template-regular-net-regexp_sch_sh")
        self.assertEqual(model.get_content(), "{template:net} 0.5 template-regular-net-regexp_sch_sh")
        
    def test_validation(self):
        """Test line validation for AF lines."""
        
        # Invalid AF line - missing value
        model = AfLineModel("{template:net}")
        self.assertEqual(model.get_status(), LineModelInterface.INVALID)
        
        # Invalid AF line - wrong format
        model = AfLineModel("template net 0.5")
        self.assertEqual(model.get_status(), LineModelInterface.INVALID)
        
        # Comment line
        model = AfLineModel("# {template:net} 0.5")
        self.assertEqual(model.get_status(), LineModelInterface.COMMENT)

        model = AfLineModel("{template:net} 0.5 template-regular-net-regexp_sch_em_sh")
        # zero matches
        self.assertEqual(model.get_status(), LineModelInterface.WARNING)

        # Valid AF line
        model = AfLineModel("{template:net} 0.5")
        # simulate the pattern matching service so that we expect a valid status
        model.set_matches((['template:net1', 'template:net2'], ['template']))
        self.assertEqual(model.get_matches(), {'nets': ['template:net1', 'template:net2'], 'templates': ['template']})
        self.assertEqual(model.get_status(), LineModelInterface.VALID)

        model = AfLineModel("{template:net} 0.5 template-regular-net-regexp_sch_em_sh")
        # simulate the pattern matching service so that we expect a valid status
        model.set_matches((['template:net1', 'template:net2'], ['template']))
        self.assertEqual(model.get_matches(), {'nets': ['template:net1', 'template:net2'], 'templates': ['template']})
        self.assertEqual(model.get_status(), LineModelInterface.VALID)
        
    def test_parse_af_line(self):
        """Test parsing AF line components."""
        model = AfLineModel("{template:net} 0.5 template-regexp-net-regular_sch_em")
        
        # Test that the components are parsed correctly
        self.assertEqual(model.get_template(), "template")
        self.assertEqual(model.get_net(), "net")
        self.assertEqual(model.get_af_value(), "0.5")
        self.assertTrue(model.is_template_regex())
        self.assertFalse(model.is_net_regex())
        self.assertTrue(model.is_em_enabled())
        self.assertFalse(model.is_sh_enabled())
        
        # Test with different flags
        model = AfLineModel("{template:net} 0.123 template-regular-net-regexp_sch_sh")
        self.assertFalse(model.is_template_regex())
        self.assertTrue(model.is_net_regex())
        self.assertEqual(model.get_af_value(), "0.123")
        self.assertFalse(model.is_em_enabled())
        self.assertTrue(model.is_sh_enabled())
        
    def test_matches_handling(self):
        """Test setting and getting matches."""
        model = AfLineModel("{template:net} 0.5")
        
        # Initially, matches should be empty
        initial_matches = model.get_matches()
        self.assertEqual(initial_matches, {'templates': [], 'nets': []})
        
        # Test setting matches
        test_matches = (['template1:net1', 'template2:net2'], ['template1', 'template2'])
        model.set_matches(test_matches)
        
        # Verify that matches were set correctly
        updated_matches = model.get_matches()
        self.assertEqual(updated_matches['nets'], ['template1:net1', 'template2:net2'])
        self.assertEqual(updated_matches['templates'], ['template1', 'template2'])
        
        # Test that get_matches returns a copy to prevent direct modification (aliasing)
        updated_matches['nets'].append('should_not_affect_original')
        self.assertNotIn('should_not_affect_original', model.get_matches()['nets'])


if __name__ == '__main__':
    unittest.main()
