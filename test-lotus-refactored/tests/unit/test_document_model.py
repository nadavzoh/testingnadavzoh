"""Unit tests for the DocumentModel class."""
import os
import unittest
import tempfile
from unittest.mock import MagicMock, patch

from src.core.models.DocumentModel import DocumentModel
from src.core.models.BasicLineModelFactory import BasicLineModelFactory


class TestDocumentModel(unittest.TestCase):
    """Test case for the DocumentModel class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.model = DocumentModel()
        self.line_model_factory = BasicLineModelFactory()
        self.model.set_line_model_factory(self.line_model_factory)
        
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
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Remove the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_load_file(self):
        """Test loading a file."""
        # Test loading a file that exists
        result = self.model.load_file(self.temp_file.name)
        self.assertTrue(result)
        self.assertEqual(self.model.get_file_path(), self.temp_file.name)
        self.assertEqual(self.model.get_line_count(), len(self.test_content))
        self.assertEqual(self.model.get_all_lines(), self.test_content)
        
        # Test loading a file that doesn't exist
        result = self.model.load_file("nonexistent_file.txt")
        self.assertFalse(result)
    
    def test_save_file(self):
        """Test saving a file."""
        # Load the test file first
        self.model.load_file(self.temp_file.name)
        
        # Modify the content
        self.model.edit_line("Modified line", 0)
        
        # Save to a new file
        new_file = self.temp_file.name + ".new"
        result = self.model.save_file(new_file)
        self.assertTrue(result)
        
        # Verify the content was saved correctly
        with open(new_file, 'r') as f:
            content = f.read().splitlines()
        self.assertEqual(content[0], "Modified line")

        # Verify the old file remains unchanged
        with open(self.temp_file.name, 'r') as f:
            original_content = f.read().splitlines()
        self.assertEqual(original_content[0], "Line 1")
        self.assertNotEqual(original_content[0], "Modified line")
        
        # Clean up
        if os.path.exists(new_file):
            os.unlink(new_file)
    
    def test_edit_line(self):
        """Test editing a line."""
        # Load the test file
        self.model.load_file(self.temp_file.name)
        
        # Edit a line
        new_content = "Modified line 2"
        result = self.model.edit_line(new_content, 1)
        self.assertTrue(result)
        self.assertEqual(self.model.get_line(1), new_content)
        
        # Test editing with invalid index
        result = self.model.edit_line("Invalid", -1)
        self.assertFalse(result)
        result = self.model.edit_line("Invalid", 100)
        self.assertFalse(result)
    
    def test_insert_line(self):
        """Test inserting a line."""
        # Load the test file
        self.model.load_file(self.temp_file.name)
        
        # Insert a line
        new_line = "New inserted line"
        result = self.model.insert_line(new_line, 2)
        self.assertTrue(result)
        self.assertEqual(self.model.get_line(2), new_line)
        self.assertEqual(self.model.get_line_count(), len(self.test_content) + 1)
        
        # Test inserting at the end
        result = self.model.insert_line("End line")
        self.assertTrue(result)
        self.assertEqual(self.model.get_line(self.model.get_line_count() - 1), "End line")
    
    def test_delete_line(self):
        """Test deleting a line."""
        # Load the test file
        self.model.load_file(self.temp_file.name)
        
        # Get the line that will be deleted
        line_to_delete = self.model.get_line(1)
        
        # Delete a line
        result = self.model.delete_line(1)
        self.assertTrue(result)
        self.assertNotEqual(self.model.get_line(1), line_to_delete)
        self.assertEqual(self.model.get_line_count(), len(self.test_content) - 1)
        
        # Test deleting with invalid index
        result = self.model.delete_line(-1)
        self.assertFalse(result)
        result = self.model.delete_line(100)
        self.assertFalse(result)
    
    def test_toggle_comment(self):
        """Test toggling comment status on a line."""
        # Load the test file
        self.model.load_file(self.temp_file.name)
        
        # Comment an uncommented line
        result = self.model.toggle_comment(0)
        self.assertTrue(result)
        self.assertTrue(self.model.get_line(0).startswith("# "))
        
        # Uncomment a commented line
        result = self.model.toggle_comment(3)  # "# Comment line"
        self.assertTrue(result)
        self.assertEqual(self.model.get_line(3), "Comment line")
    
    def test_duplicate_line(self):
        """Test duplicating a line."""
        # Load the test file
        self.model.load_file(self.temp_file.name)
        
        # Duplicate a line
        line_to_duplicate = self.model.get_line(1)
        result = self.model.duplicate_line(1)
        self.assertTrue(result)
        self.assertEqual(self.model.get_line(2), line_to_duplicate)
        self.assertEqual(self.model.get_line_count(), len(self.test_content) + 1)
    
    def test_move_line(self):
        """Test moving lines up and down."""
        # Load the test file
        self.model.load_file(self.temp_file.name)
        
        # Move a line up
        line1 = self.model.get_line(1)
        line2 = self.model.get_line(2)
        result = self.model.move_line_up(2)
        self.assertTrue(result)
        self.assertEqual(self.model.get_line(1), line2)
        self.assertEqual(self.model.get_line(2), line1)
        
        # Move a line down
        line1 = self.model.get_line(1)
        line2 = self.model.get_line(2)
        result = self.model.move_line_down(1)
        self.assertTrue(result)
        self.assertEqual(self.model.get_line(1), line2)
        self.assertEqual(self.model.get_line(2), line1)
        
        # Test moving with invalid indices
        result = self.model.move_line_up(0)
        self.assertFalse(result)
        result = self.model.move_line_down(self.model.get_line_count() - 1)
        self.assertFalse(result)
    
    def test_undo_redo(self):
        """Test undo and redo functionality."""
        # Load the test file
        self.model.load_file(self.temp_file.name)
        
        # Perform some actions
        original_line = self.model.get_line(0)
        self.model.edit_line("Modified line", 0)
        self.model.insert_line("New line", 1)
        self.model.delete_line(2)
        
        # Undo the delete
        self.assertTrue(self.model.can_undo())
        result = self.model.undo()
        self.assertTrue(result)
        self.assertEqual(self.model.get_line_count(), len(self.test_content) + 1)
        
        # Undo the insert
        result = self.model.undo()
        self.assertTrue(result)
        self.assertEqual(self.model.get_line_count(), len(self.test_content))
        
        # Undo the edit
        result = self.model.undo()
        self.assertTrue(result)
        self.assertEqual(self.model.get_line(0), original_line)
        
        # Redo the edit
        self.assertTrue(self.model.can_redo())
        result = self.model.redo()
        self.assertTrue(result)
        self.assertEqual(self.model.get_line(0), "Modified line")
        
        # Redo the insert
        result = self.model.redo()
        self.assertTrue(result)
        self.assertEqual(self.model.get_line_count(), len(self.test_content) + 1)
        
        # Redo the delete
        result = self.model.redo()
        self.assertTrue(result)
        self.assertEqual(self.model.get_line_count(), len(self.test_content))


if __name__ == '__main__':
    unittest.main()
