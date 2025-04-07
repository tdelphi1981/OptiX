from base.OXception import OXception


def get_fully_qualified_name(cls: type) -> str:
    """Get the fully qualified name of a class.

    The fully qualified name includes the module path and the class name,
    separated by a dot.

    Args:
        cls (type): The class to get the name for.

    Returns:
        str: The fully qualified name of the class.

    Examples:
        >>> from base.OXObject import OXObject
        >>> get_fully_qualified_name(OXObject)
        'base.OXObject'

    See Also:
        :func:`load_class`
    """
    return cls.__module__ + "." + cls.__name__

def load_class(fully_qualified_name: str) -> type:
    """Load a class given its fully qualified name.

    This function dynamically imports a module and gets a class from it.

    Args:
        fully_qualified_name (str): The fully qualified name of the class to load.

    Returns:
        type: The loaded class.

    Raises:
        OXception: If the class is not found or if there's an error loading it.

    Examples:
        >>> cls = load_class("base.OXObject")
        >>> obj = cls()
        >>> print(obj.class_name)
        base.OXObject

    See Also:
        :func:`get_fully_qualified_name`
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
