"""Unit tests for line model classes."""
import unittest

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
        model = AfLineModel("{template:net} 0.5")
        self.assertEqual(model.get_content(), "{template:net} 0.5")
        
    def test_validation(self):
        """Test line validation for AF lines."""
        # Valid AF line
        model = AfLineModel("{template:net} 0.5")
        self.assertEqual(model.get_status(), LineModelInterface.VALID)
        
        # Invalid AF line - missing value
        model = AfLineModel("{template:net}")
        self.assertEqual(model.get_status(), LineModelInterface.INVALID)
        
        # Invalid AF line - wrong format
        model = AfLineModel("template net 0.5")
        self.assertEqual(model.get_status(), LineModelInterface.INVALID)
        
        # Comment line
        model = AfLineModel("# {template:net} 0.5")
        self.assertEqual(model.get_status(), LineModelInterface.COMMENT)
        
    def test_parse_af_line(self):
        """Test parsing AF line components."""
        model = AfLineModel("{template:net} 0.5 template-regexp _em")
        
        # Test that the components are parsed correctly
        self.assertEqual(model.get_template(), "template")
        self.assertEqual(model.get_net(), "net")
        self.assertEqual(model.get_af_value(), "0.5")
        self.assertTrue(model.is_template_regex())
        self.assertFalse(model.is_net_regex())
        self.assertTrue(model.is_em_enabled())
        self.assertFalse(model.is_sh_enabled())
        
        # Test with different flags
        model = AfLineModel("{template:net} 0.5 net-regexp _sh")
        self.assertFalse(model.is_template_regex())
        self.assertTrue(model.is_net_regex())
        self.assertFalse(model.is_em_enabled())
        self.assertTrue(model.is_sh_enabled())


if __name__ == '__main__':
    unittest.main()
