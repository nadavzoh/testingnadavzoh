"""Unit tests for line model factory classes."""
import unittest
from unittest.mock import patch, MagicMock

from src.core.models.LineModelInterface import LineModelInterface
from src.core.models.BasicLineModelFactory import BasicLineModelFactory
from src.core.models.AfLineModelFactory import AfLineModelFactory
from src.core.models.BasicLineModel import BasicLineModel
from src.core.models.AfLineModel import AfLineModel
from src.core.services.ServiceLocator import ServiceLocator


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
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock PatternMatchingService
        self.mock_service = MagicMock()
        self.mock_service.find_matches.return_value = (
            ['template1:net1', 'template2:net2'],  # net matches
            ['template1', 'template2']            # template matches
        )
        
        # Clear the ServiceLocator registry before each test
        ServiceLocator._services = {}
    
    def test_create_line_model_without_pattern_matching_service(self):
        """Test creating an AfLineModel without a pattern matching service."""
        factory = AfLineModelFactory()
        line_model = factory.create_line_model("{template:net} 0.5")
        
        # Check that the correct model type is created
        self.assertIsInstance(line_model, AfLineModel)
        self.assertEqual(line_model.get_content(), "{template:net} 0.5")
        
        # Without a pattern matching service, matches should be empty
        self.assertEqual(line_model.get_matches(), {'templates': [], 'nets': []})
    
    @patch('src.core.services.ServiceLocator.ServiceLocator.is_registered')
    @patch('src.core.services.ServiceLocator.ServiceLocator.get')
    def test_create_line_model_with_pattern_matching_service(self, mock_get, mock_is_registered):
        """Test creating an AfLineModel with a pattern matching service."""
        # Configure mocks
        mock_is_registered.return_value = True
        mock_get.return_value = self.mock_service
        
        factory = AfLineModelFactory()
        line_model = factory.create_line_model("{template:net} 0.5")
        
        # Check that the correct model type is created
        self.assertIsInstance(line_model, AfLineModel)
        self.assertEqual(line_model.get_content(), "{template:net} 0.5")
        
        # Verify that the service locator was used to get the pattern matching service
        mock_is_registered.assert_called_with('pattern_matching_service')
        mock_get.assert_called_with('pattern_matching_service')
        
        # Verify that find_matches was called with the correct parameters
        self.mock_service.find_matches.assert_called_with(
            "template", "net", False, False
        )
        
        # Check that matches were set on the model
        matches = line_model.get_matches()
        self.assertEqual(matches['nets'], ['template1:net1', 'template2:net2'])
        self.assertEqual(matches['templates'], ['template1', 'template2'])
    
    @patch('src.core.services.ServiceLocator.ServiceLocator.is_registered')
    @patch('src.core.services.ServiceLocator.ServiceLocator.get')
    def test_create_line_model_with_regex_flags(self, mock_get, mock_is_registered):
        """Test creating an AfLineModel with regex flags enabled."""
        # Configure mocks
        mock_is_registered.return_value = True
        mock_get.return_value = self.mock_service
        
        factory = AfLineModelFactory()
        line_model = factory.create_line_model("{template:net} 0.5 template-regexp-net-regexp_sch_em")
        
        # Verify that find_matches was called with regex flags set to True
        self.mock_service.find_matches.assert_called_with(
            "template", "net", True, True
        )
    
    def test_create_line_model_with_comment_line(self):
        """Test creating an AfLineModel with a comment line."""
        factory = AfLineModelFactory()
        line_model = factory.create_line_model("# {template:net} 0.5")
        
        # Check that the line is recognized as a comment
        self.assertEqual(line_model.get_status(), LineModelInterface.COMMENT)
        
        # For comment lines, matches should not be set
        self.assertEqual(line_model.get_matches(), {'templates': [], 'nets': []})


if __name__ == '__main__':
    unittest.main()
