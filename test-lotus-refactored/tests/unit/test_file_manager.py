"""Unit tests for the FileManager class."""
import os
import unittest
import tempfile


from src.core.models.FileManager import FileManager


class TestFileManager(unittest.TestCase):
    """Test case for the FileManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.file_manager = FileManager()
        
        # Create a temporary test file
        self.test_content = [
            "Line 1",
            "Line 2",
            "Line 3",
            "# Comment line",
            "Line 5"
        ]
        
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        self.temp_file.write('\n'.join(self.test_content))
        self.temp_file.close()
        
        # Create a temporary AF file
        self.af_content = [
            "# Activity Factor configuration",
            "{template1:net1} 0.5",
            "{template2:net2} 0.3 template-regexp",
            "{template3:net3} 0.7 _em"
        ]
        
        self.af_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.af.dcfg')
        self.af_file.write('\n'.join(self.af_content))
        self.af_file.close()
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Remove the temporary files
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        if os.path.exists(self.af_file.name):
            os.unlink(self.af_file.name)
    
    def test_load_file(self):
        """Test loading a file."""
        # Test loading a file that exists
        success, content, error = self.file_manager.load_file(self.temp_file.name)
        self.assertTrue(success)
        self.assertEqual(content, self.test_content)
        self.assertIsNone(error)
        
        # Test loading a file that doesn't exist
        success, content, error = self.file_manager.load_file("nonexistent_file.txt")
        self.assertFalse(success)
        self.assertIsNotNone(error)
    
    def test_save_file(self):
        """Test saving a file."""
        # Modify the content
        modified_content = self.test_content.copy()
        modified_content[0] = "Modified line"
        
        # Save to a new file
        new_file = self.temp_file.name + ".new"
        success, error = self.file_manager.save_file(new_file, modified_content)
        self.assertTrue(success)
        self.assertIsNone(error)
        
        # Verify the content was saved correctly
        with open(new_file, 'r') as f:
            content = f.read().splitlines()
        self.assertEqual(content[0], "Modified line")
        
        # Clean up
        if os.path.exists(new_file):
            os.unlink(new_file)
    
    def test_get_file_type(self):
        """Test getting the file type."""
        # Test AF file type
        file_type = self.file_manager.get_file_type(self.af_file.name)
        self.assertEqual(file_type, "af")
        
        # Test text file type
        text_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt')
        text_file.close()
        file_type = self.file_manager.get_file_type(text_file.name)
        self.assertEqual(file_type, "text")
        
        # Test unknown file type
        unknown_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.xyz')
        unknown_file.close()
        file_type = self.file_manager.get_file_type(unknown_file.name)
        self.assertIsNone(file_type)
        
        # Clean up
        if os.path.exists(text_file.name):
            os.unlink(text_file.name)
        if os.path.exists(unknown_file.name):
            os.unlink(unknown_file.name)


if __name__ == '__main__':
    unittest.main()
