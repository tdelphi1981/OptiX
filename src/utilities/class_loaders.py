"""
Dynamic Class Loading Utilities Module
======================================

This module provides simple utilities for dynamic class loading within the OptiX 
optimization framework. It contains two basic functions that support object 
serialization and deserialization by enabling runtime class resolution.

Key Functions:
    - **get_fully_qualified_name**: Generate module.ClassName strings
    - **load_class**: Dynamically load classes from module.ClassName strings

Example:
    Basic usage for class identification and dynamic loading:

    .. code-block:: python

        from utilities.class_loaders import get_fully_qualified_name, load_class
        from base.OXObject import OXObject
        
        # Get module.ClassName string
        class_id = get_fully_qualified_name(OXObject)
        print(class_id)  # Output: 'base.OXObject.OXObject'
        
        # Dynamically load the class
        loaded_class = load_class(class_id)
        instance = loaded_class()
        
        # Verify roundtrip integrity
        assert loaded_class == OXObject

Module Dependencies:
    - base.OXception: Framework-specific exception handling
"""

from base.OXception import OXception


def get_fully_qualified_name(cls: type) -> str:
    """
    Generate a fully qualified name string for a Python class.
    
    This function creates a string representation of a class by concatenating
    the module name and class name with a dot separator. The result can be
    used with the :func:`load_class` function to dynamically load the class.

    Args:
        cls (type): The class object to generate a name for.

    Returns:
        str: A string in the format ``module_name.ClassName``.

    Examples:
        Generate fully qualified names for classes:
        
        .. code-block:: python
        
            from base.OXObject import OXObject
            
            # Get the class name string
            name = get_fully_qualified_name(OXObject)
            print(name)  # Output: 'base.OXObject.OXObject'
            
            # Works with built-in types too
            list_name = get_fully_qualified_name(list)
            print(list_name)  # Output: 'builtins.list'

    See Also:
        :func:`load_class`: Load a class from its fully qualified name.
    """
    return cls.__module__ + "." + cls.__name__

def load_class(fully_qualified_name: str) -> type:
    """
    Dynamically load a Python class from its fully qualified name.
    
    This function loads a class by parsing the fully qualified name string,
    importing the module, and retrieving the class object from the module.

    Args:
        fully_qualified_name (str): The fully qualified name of the class to load
                                   in the format ``module.ClassName``.

    Returns:
        type: The loaded class object.

    Raises:
        OXception: If the class cannot be loaded due to import errors or
                  missing class names.

    Examples:
        Load classes dynamically:
        
        .. code-block:: python
        
            # Load a framework class
            obj_class = load_class("base.OXObject.OXObject")
            instance = obj_class()
            
            # Roundtrip demonstration
            from base.OXObject import OXObject
            name = get_fully_qualified_name(OXObject)
            loaded_class = load_class(name)
            assert loaded_class is OXObject

    See Also:
        :func:`get_fully_qualified_name`: Generate class names for use with this function.
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
