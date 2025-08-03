"""Utilities package for the OptiX optimization framework.

This package provides utility functions and helper classes used throughout the
OptiX framework. It includes functionality for dynamic class loading, reflection,
and other common operations that support the framework's core functionality.

The utilities package is designed to be lightweight and focused on providing
essential support functions that are used by multiple components of the framework.

Modules:
    class_loaders: Dynamic class loading and reflection utilities.

Functions:
    get_fully_qualified_name: Get the fully qualified name of a class.
    load_class: Dynamically load a class from its fully qualified name.

Key Features:
    - Dynamic class loading with proper error handling
    - Reflection utilities for class introspection
    - Fully qualified name generation for class identification
    - Exception handling with framework-specific error types

Examples:
    >>> from utilities import get_fully_qualified_name, load_class
    >>> from base import OXObject
    >>> 
    >>> # Get fully qualified name of a class
    >>> name = get_fully_qualified_name(OXObject)
    >>> print(name)  # Output: base.OXObject
    >>> 
    >>> # Load a class dynamically
    >>> cls = load_class("base.OXObject")
    >>> obj = cls()
    >>> print(obj.class_name)  # Output: base.OXObject

The utilities in this package are particularly useful for:
- Serialization and deserialization operations
- Plugin-style architecture implementations
- Dynamic object creation based on configuration
- Framework extensibility mechanisms

See Also:
    :mod:`base`: Base classes and exceptions used by utilities.
    :mod:`serialization`: Uses utilities for dynamic class loading.
"""

from .class_loaders import (
    get_fully_qualified_name,
    load_class
)