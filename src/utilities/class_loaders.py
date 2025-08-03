"""
Dynamic Class Loading Utilities Module
======================================

This module provides utilities for dynamic class loading and reflection operations 
within the OptiX optimization framework. It enables runtime class discovery, loading,
and name resolution, which are essential for serialization, deserialization, and
plugin-style architecture implementations.

The module implements safe dynamic class loading with comprehensive error handling
and validation to ensure robust operation across the framework's components.

Key Functions:
    - **get_fully_qualified_name**: Generate standardized class identifiers
    - **load_class**: Dynamically load classes from their fully qualified names

Use Cases:
    - Serialization and deserialization of complex object hierarchies
    - Plugin-style architecture with runtime class discovery
    - Configuration-driven object instantiation
    - Framework extensibility mechanisms
    - Type preservation across serialization boundaries

Example:
    Basic usage for class identification and dynamic loading:

    .. code-block:: python

        from utilities.class_loaders import get_fully_qualified_name, load_class
        from base.OXObject import OXObject
        
        # Get standardized class identifier
        class_id = get_fully_qualified_name(OXObject)
        print(class_id)  # Output: 'base.OXObject'
        
        # Dynamically load the class
        loaded_class = load_class(class_id)
        instance = loaded_class()
        
        # Verify roundtrip integrity
        assert loaded_class == OXObject

Module Dependencies:
    - base.OXception: Framework-specific exception handling
    - Python importlib: Dynamic module importing capabilities
"""

from base.OXception import OXception


def get_fully_qualified_name(cls: type) -> str:
    """
    Generate a standardized fully qualified name for a Python class.
    
    This function creates a canonical string representation of a class that includes
    the complete module path and class name. The generated identifier is deterministic
    and can be used for class reconstruction via the :func:`load_class` function.
    
    The fully qualified name format follows Python's standard module.Class naming
    convention and is essential for maintaining type information across serialization
    boundaries and enabling dynamic class loading throughout the OptiX framework.

    Args:
        cls (type): The class object to generate a fully qualified name for.
                   Must be a valid Python class or type object with accessible
                   ``__module__`` and ``__name__`` attributes.

    Returns:
        str: A standardized fully qualified name in the format ``module.path.ClassName``.
             This string identifier can be used with :func:`load_class` to reconstruct
             the original class object.

    Raises:
        AttributeError: If the provided class object lacks ``__module__`` or ``__name__``
                       attributes (though this is extremely rare for valid Python classes).

    Note:
        - The generated name is deterministic and will always be the same for the same class
        - This function is thread-safe and has no side effects
        - The format is compatible with Python's import system and reflection mechanisms
        - Used extensively in OptiX serialization and deserialization processes

    Examples:
        Generate fully qualified names for framework classes:
        
        .. code-block:: python
        
            from base.OXObject import OXObject
            from problem.OXProblem import OXLPProblem
            
            # Core framework class
            base_name = get_fully_qualified_name(OXObject)
            print(base_name)  # Output: 'base.OXObject'
            
            # Problem class with nested module structure
            problem_name = get_fully_qualified_name(OXLPProblem)
            print(problem_name)  # Output: 'problem.OXProblem.OXLPProblem'
            
            # Works with built-in types too
            list_name = get_fully_qualified_name(list)
            print(list_name)  # Output: 'builtins.list'

    See Also:
        :func:`load_class`: Reverse operation to reconstruct a class from its fully qualified name.
    """
    return cls.__module__ + "." + cls.__name__

def load_class(fully_qualified_name: str) -> type:
    """
    Dynamically load a Python class from its fully qualified name.
    
    This function performs runtime class loading by parsing a fully qualified class name,
    dynamically importing the required module, and retrieving the class object. It serves
    as the reverse operation of :func:`get_fully_qualified_name` and is essential for
    deserialization, plugin loading, and configuration-driven object instantiation.
    
    The loading process implements a robust multi-step approach:
    1. Parse the fully qualified name to extract module and class components
    2. Dynamically import the module using Python's import system
    3. Retrieve the class object from the imported module using attribute access
    4. Validate the class exists and return the loaded class object
    
    All operations include comprehensive error handling to provide meaningful feedback
    when class loading fails due to import errors, missing classes, or other issues.

    Args:
        fully_qualified_name (str): The fully qualified name of the class to load.
                                   Must follow the format ``module.path.ClassName`` where
                                   the module path is importable and the class name exists
                                   within that module. Should typically be generated by
                                   :func:`get_fully_qualified_name`.

    Returns:
        type: The dynamically loaded class object that can be used to create instances
              or perform class-level operations. The returned class is identical to
              what would be obtained through direct import statements.

    Raises:
        OXception: If the specified class cannot be found in the target module.
                  This typically indicates a typo in the class name or the class
                  has been removed or renamed.
        OXception: If there's an error during module import (e.g., ModuleNotFoundError,
                  ImportError, syntax errors in the module). The original exception
                  details are preserved in the error message for debugging.
        OXception: If the fully qualified name format is invalid (e.g., missing dots,
                  empty components). This indicates malformed input data.

    Security:
        This function dynamically imports modules and should only be used with trusted
        fully qualified names. Malicious module names could potentially execute
        arbitrary code during import.

    Performance:
        - Module imports are cached by Python's import system
        - Subsequent loads of the same class are fast due to import caching
        - Class attribute access is optimized by Python's attribute lookup mechanism

    Examples:
        Load various framework classes dynamically:
        
        .. code-block:: python
        
            # Load a core framework class
            obj_class = load_class("base.OXObject")
            instance = obj_class()
            print(instance.uuid)  # Creates new OXObject instance
            
            # Load a problem class for optimization
            problem_class = load_class("problem.OXProblem.OXLPProblem")
            problem = problem_class("My LP Problem")
            
            # Roundtrip demonstration
            from base.OXObject import OXObject
            name = get_fully_qualified_name(OXObject)
            loaded_class = load_class(name)
            assert loaded_class is OXObject  # Same class object
            
            # Error handling example
            try:
                bad_class = load_class("nonexistent.module.BadClass")
            except OXception as e:
                print(f"Failed to load class: {e}")

    Note:
        - This function is thread-safe as Python's import system handles concurrency
        - Module imports may trigger module-level code execution
        - The function preserves the original exception context for debugging
        - Commonly used in OptiX serialization/deserialization workflows

    See Also:
        :func:`get_fully_qualified_name`: Generate standardized class names for use with this function.
    """
    try:
        module_name, class_name = fully_qualified_name.rsplit(".", 1)
        module = __import__(module_name, fromlist=[class_name])
        retval = getattr(module, class_name)
        if retval is None:
            raise OXception(f"Class {fully_qualified_name} not found")
        return retval
    except Exception as e:
        if isinstance(e, OXception):
            raise e
        raise OXception(f"Error loading class {fully_qualified_name}: {e}")
