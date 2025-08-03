from base.OXception import OXception


def get_fully_qualified_name(cls: type) -> str:
    """Get the fully qualified name of a class.

    The fully qualified name includes the module path and the class name,
    separated by a dot. This format is compatible with the :func:`load_class`
    function and is used throughout the OptiX framework for class identification
    and serialization.

    The function constructs the name by combining the class's ``__module__``
    attribute with its ``__name__`` attribute, separated by a dot.

    Args:
        cls (type): The class object to get the fully qualified name for.
            Must be a valid Python class or type object.

    Returns:
        str: The fully qualified name of the class in the format
            ``module.path.ClassName``. This string can be used to
            reconstruct the class using :func:`load_class`.

    Examples:
        >>> from base.OXObject import OXObject
        >>> name = get_fully_qualified_name(OXObject)
        >>> print(name)
        'base.OXObject'
        >>> 
        >>> # Works with any class
        >>> from problem.OXProblem import OXLPProblem
        >>> name = get_fully_qualified_name(OXLPProblem)
        >>> print(name)
        'problem.OXProblem.OXLPProblem'

    Note:
        This function is commonly used in serialization processes where
        class type information needs to be preserved and later reconstructed.

    See Also:
        :func:`load_class`: Reverse operation to load a class from its name.
    """
    return cls.__module__ + "." + cls.__name__

def load_class(fully_qualified_name: str) -> type:
    """Load a class given its fully qualified name.

    This function dynamically imports a module and retrieves a class from it
    using the fully qualified name format (``module.path.ClassName``). It performs
    the reverse operation of :func:`get_fully_qualified_name`.

    The loading process involves:
    1. Splitting the fully qualified name into module and class components
    2. Dynamically importing the module using ``__import__``
    3. Retrieving the class object using ``getattr``
    4. Validating that the class was found

    Args:
        fully_qualified_name (str): The fully qualified name of the class to load.
            Must be in the format ``module.path.ClassName`` where the module
            path is importable and the class name exists within that module.

    Returns:
        type: The loaded class object that can be used to create instances.
            The returned class will be the same type as the original class
            that was used to generate the fully qualified name.

    Raises:
        OXception: If the class is not found in the specified module.
        OXception: If there's an error during module import or class retrieval.
            The original exception details are included in the error message.

    Examples:
        >>> # Load a base class
        >>> cls = load_class("base.OXObject")
        >>> obj = cls()
        >>> print(obj.class_name)
        base.OXObject
        >>> 
        >>> # Load a problem class
        >>> problem_cls = load_class("problem.OXProblem.OXLPProblem")
        >>> problem = problem_cls()
        >>> print(type(problem).__name__)
        OXLPProblem
        >>> 
        >>> # Roundtrip example
        >>> from base.OXObject import OXObject
        >>> name = get_fully_qualified_name(OXObject)
        >>> loaded_cls = load_class(name)
        >>> print(loaded_cls == OXObject)
        True

    Note:
        This function is essential for deserialization processes where class
        type information needs to be reconstructed from stored metadata.
        It provides a safe way to dynamically load classes with proper
        error handling.

    See Also:
        :func:`get_fully_qualified_name`: Generate the names used by this function.
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
