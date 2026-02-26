#!/usr/bin/env python3
"""Test runner for capturing-events skill with hyphenated directory support."""
import sys
import os
import unittest
import importlib.util

# Add the pax directory to path
pax_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pax_root)

# Utility to load modules from hyphenated directory names
def load_module_from_path(module_name, file_path):
    """Load a Python module from a file path, handling hyphenated names."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load modules from capturing-events directory
skill_dir = os.path.join(pax_root, 'skills/tools/capturing-events')
tests_dir = os.path.join(skill_dir, 'tests')

# Load event_schema
event_schema_path = os.path.join(skill_dir, 'event_schema.py')
event_schema = load_module_from_path('event_schema', event_schema_path)

# Load providers
providers_dir = os.path.join(skill_dir, 'providers')
universal_path = os.path.join(providers_dir, 'universal.py')
universal = load_module_from_path('universal', universal_path)

# Load storage
storage_dir = os.path.join(skill_dir, 'storage')
jsonl_handler_path = os.path.join(storage_dir, 'jsonl_handler.py')
jsonl_handler = load_module_from_path('jsonl_handler', jsonl_handler_path)

# Load test modules
test_event_capture_path = os.path.join(tests_dir, 'test_event_capture.py')
test_storage_path = os.path.join(tests_dir, 'test_storage.py')

test_event_capture = load_module_from_path('test_event_capture', test_event_capture_path)
test_storage = load_module_from_path('test_storage', test_storage_path)

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
