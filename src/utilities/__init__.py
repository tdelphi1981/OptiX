"""
Utilities Module
================

This module provides utility functions for dynamic class loading within the OptiX 
optimization framework. It contains simple helper functions that support object 
serialization and deserialization by enabling runtime class resolution.

Core Functions:
    - **get_fully_qualified_name**: Generate module.ClassName strings for classes
    - **load_class**: Dynamically load classes from module.ClassName strings

Usage:
    Import utility functions for dynamic class operations:

    .. code-block:: python

        from utilities import get_fully_qualified_name, load_class
        from base.OXObject import OXObject
        
        # Generate module.ClassName string
        class_id = get_fully_qualified_name(OXObject)
        print(class_id)  # Output: 'base.OXObject.OXObject'
        
        # Dynamically load the class
        loaded_class = load_class(class_id)
        instance = loaded_class()
        
        # Verify roundtrip integrity
        assert loaded_class is OXObject

See Also:
    :mod:`base`: Base classes and exceptions used by utility functions.
    :mod:`serialization`: Uses dynamic class loading for object persistence.
"""

from .class_loaders import (
    get_fully_qualified_name,
    load_class
)

__all__ = [
    "get_fully_qualified_name",
    "load_class",
]