#!/usr/bin/env python3
"""Test runner for capture-events skill with proper module discovery."""
import sys
import os
import unittest

# Add the pax directory to path so relative imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import test modules
try:
    from skills.tools.capture_events.tests import test_event_capture, test_storage
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all tests from both modules
    suite.addTests(loader.loadTestsFromModule(test_event_capture))
    suite.addTests(loader.loadTestsFromModule(test_storage))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)
