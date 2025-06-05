#!/usr/bin/env python3
"""Test runner for Lotus unit tests."""
import unittest
import sys
import os

# Add the parent directory to the path so that imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Import all test modules
from tests.unit.test_document_model import TestDocumentModel
from tests.unit.test_line_models import TestBasicLineModel, TestAfLineModel
from tests.unit.test_line_model_factories import TestBasicLineModelFactory, TestAfLineModelFactory


def create_test_suite():
    """Create a test suite containing all tests."""
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    # Add DocumentModel tests
    suite.addTest(loader.loadTestsFromTestCase(TestDocumentModel))
    
    # Add line model tests
    suite.addTest(loader.loadTestsFromTestCase(TestBasicLineModel))
    suite.addTest(loader.loadTestsFromTestCase(TestAfLineModel))
    
    # Add factory tests
    suite.addTest(loader.loadTestsFromTestCase(TestBasicLineModelFactory))
    suite.addTest(loader.loadTestsFromTestCase(TestAfLineModelFactory))
    
    return suite


if __name__ == '__main__':
    # Create the test suite
    suite = create_test_suite()
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return non-zero exit code if tests failed
    sys.exit(not result.wasSuccessful())
