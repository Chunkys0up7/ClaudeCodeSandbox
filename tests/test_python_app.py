#!/usr/bin/env python3
"""
Test suite for the Python components of the AI App Store
"""

import unittest
import sys
import os

# Add the src directory to the path so we can import the app module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.python.app import AIAppStore

class TestAIAppStore(unittest.TestCase):
    """Test cases for the AIAppStore class"""
    
    def setUp(self):
        """Set up test environment"""
        self.store = AIAppStore()
    
    def test_init(self):
        """Test initialization"""
        self.assertEqual(len(self.store.apps), 0)
        self.assertEqual(len(self.store.users), 0)
    
    def test_register_app(self):
        """Test app registration"""
        app = {"name": "Test App", "description": "Test Description"}
        result = self.store.register_app(app)
        self.assertTrue(result)
        self.assertEqual(len(self.store.apps), 1)
    
    def test_list_apps(self):
        """Test listing apps"""
        apps = self.store.list_apps()
        self.assertEqual(len(apps), 0)
        
        # Register an app
        app = {"name": "Test App", "description": "Test Description"}
        self.store.register_app(app)
        
        # Check if the app was registered
        apps = self.store.list_apps()
        self.assertEqual(len(apps), 1)

if __name__ == "__main__":
    unittest.main()
