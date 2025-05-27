"""Unit tests for line model factory classes."""
import unittest

from src.core.models.LineModelInterface import LineModelInterface
from src.core.models.BasicLineModelFactory import BasicLineModelFactory
from src.core.models.AfLineModelFactory import AfLineModelFactory
from src.core.models.BasicLineModel import BasicLineModel
from src.core.models.AfLineModel import AfLineModel


class TestBasicLineModelFactory(unittest.TestCase):
    """Test case for the BasicLineModelFactory class."""
    
    def test_create_line_model(self):
        """Test creating a BasicLineModel."""
        factory = BasicLineModelFactory()
        line_model = factory.create_line_model("Test line")
        
        # Check that the correct model type is created
        self.assertIsInstance(line_model, BasicLineModel)
        self.assertEqual(line_model.get_content(), "Test line")
        
        # Test with comment line
        line_model = factory.create_line_model("# Comment")
        self.assertEqual(line_model.get_status(), LineModelInterface.COMMENT)


class TestAfLineModelFactory(unittest.TestCase):
    """Test case for the AfLineModelFactory class."""
    
    def test_create_line_model(self):
        """Test creating an AfLineModel."""
        factory = AfLineModelFactory()
        line_model = factory.create_line_model("{template:net} 0.5")
        
        # Check that the correct model type is created
        self.assertIsInstance(line_model, AfLineModel)
        self.assertEqual(line_model.get_content(), "{template:net} 0.5")
        
        # Test with comment line
        line_model = factory.create_line_model("# {template:net} 0.5")
        self.assertEqual(line_model.get_status(), LineModelInterface.COMMENT)


if __name__ == '__main__':
    unittest.main()
