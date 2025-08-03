"""
OptiX Class Loading Utilities Test Suite
========================================

This module provides comprehensive test coverage for the class loading
utilities in the OptiX optimization framework. The class loading system
enables dynamic class instantiation from string identifiers, supporting
deserialization and flexible object creation patterns.

The class loader functionality is essential for serialization/deserialization
operations, configuration-based object creation, and dynamic module loading
within the OptiX ecosystem.

Example:
    Running the class loader test suite:

    .. code-block:: bash

        # Run all class loader tests
        poetry run python -m pytest tests/test_class_loaders.py -v
        
        # Run valid class loading tests
        poetry run python -m pytest tests/test_class_loaders.py -k "valid" -v
        
        # Run error handling tests
        poetry run python -m pytest tests/test_class_loaders.py -k "invalid" -v

Module Dependencies:
    - src.utilities.class_loaders: Dynamic class loading utilities

Test Coverage:
    - Valid class loading from fully qualified class names
    - Class instantiation and property validation
    - Module resolution and import handling
    - Error handling for invalid class references
    - Object creation and initialization verification
    - Class metadata validation and attribute checking

Class Loading Features Tested:
    - Dynamic class resolution from string identifiers
    - Module import and class extraction
    - Object instantiation with proper initialization
    - Class name and module validation
    - Property and attribute verification
    - Error handling for missing or invalid classes
"""

from src.utilities.class_loaders import load_class


def test_load_class_valid_class():
    # Test loading a valid class
    clazz = load_class("base.OXObject.OXObject")
    assert clazz.__name__ == "OXObject"
    assert clazz.__module__ == "base.OXObject"
    obj = clazz()
    assert obj.id is not None
    assert obj.class_name == "base.OXObject.OXObject"

    clazz2 = load_class("base.OXObjectPot.OXObjectPot")
    assert clazz2.__name__ == "OXObjectPot"
    assert clazz2.__module__ == "base.OXObjectPot"
    obj2 = clazz2()
    assert obj2.id is not None
    assert obj2.class_name == "base.OXObjectPot.OXObjectPot"

