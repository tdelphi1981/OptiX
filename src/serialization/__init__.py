"""Serialization package for the OptiX optimization framework.

This package provides functionality for serializing and deserializing OptiX objects
to and from Python dictionaries. It supports the conversion of complex object
hierarchies including nested objects and lists of objects.

The serialization process preserves object identity and class information, allowing
for complete reconstruction of the original object structure during deserialization.

Functions:
    serialize_to_python_dict: Converts an OXObject to a Python dictionary.
    deserialize_from_python_dict: Converts a Python dictionary back to an OXObject.

Key Features:
    - Preserves object class information for accurate deserialization
    - Handles nested objects and lists of objects recursively
    - Maintains object identity through UUID preservation
    - Provides error handling for malformed data structures

Examples:
    >>> from serialization import serialize_to_python_dict, deserialize_from_python_dict
    >>> from problem import OXLPProblem
    >>> 
    >>> # Create and serialize a problem
    >>> problem = OXLPProblem()
    >>> problem.create_decision_variable("x", lower_bound=0, upper_bound=10)
    >>> 
    >>> # Serialize to dictionary
    >>> problem_dict = serialize_to_python_dict(problem)
    >>> 
    >>> # Deserialize back to object
    >>> restored_problem = deserialize_from_python_dict(problem_dict)
    >>> print(restored_problem.variables[0].name)  # Output: x

The serialization format uses the object's class_name and id fields as required
metadata, with all other attributes preserved as-is or recursively serialized
if they are OXObject instances.

See Also:
    :mod:`base`: Base classes for all OptiX objects.
    :mod:`utilities.class_loaders`: Dynamic class loading utilities.
"""

from .serializers import (
    serialize_to_python_dict,
    deserialize_from_python_dict
)