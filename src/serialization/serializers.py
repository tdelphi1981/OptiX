from dataclasses import asdict

from base import OXObject
from base import OXception
from utilities.class_loaders import load_class


def serialize_to_python_dict(obj: OXObject) -> dict:
    """Serialize an OXObject to a Python dictionary.

    This function converts an OXObject to a dictionary using the asdict function
    from the dataclasses module. The resulting dictionary contains all object
    attributes including class_name and id fields required for deserialization.

    The serialization preserves the complete object state including:
    - All dataclass fields and their values
    - Object identity through the id field
    - Class information through the class_name field
    - Nested objects and collections (handled by asdict)

    Args:
        obj (OXObject): The OXObject instance to serialize. Must be a dataclass
            instance with class_name and id attributes.

    Returns:
        dict: A dictionary representation of the object containing all fields
            and their values. The dictionary will always include 'class_name'
            and 'id' keys along with any other object attributes.

    Examples:
        >>> from base import OXObject
        >>> obj = OXObject()
        >>> dct = serialize_to_python_dict(obj)
        >>> print(dct["class_name"])
        base.OXObject
        >>> print("id" in dct)
        True

    See Also:
        :func:`deserialize_from_python_dict`: Reverse operation to reconstruct objects.
        :func:`dataclasses.asdict`: Core function used for serialization.
    """
    return asdict(obj)


def deserialize_from_python_dict(dct: dict) -> OXObject:
    """Deserialize a Python dictionary to an OXObject.

    This function converts a dictionary back to an OXObject instance by reconstructing
    the original object structure. The process involves:
    
    1. Loading the class using the class_name field
    2. Creating a new instance of the class
    3. Setting the id field to preserve object identity
    4. Recursively deserializing nested dictionaries and lists of dictionaries
    5. Setting all other attributes on the object

    The function handles complex object hierarchies and nested structures by
    recursively attempting to deserialize any dictionary values it encounters.
    If deserialization fails for a nested dictionary (due to missing required fields),
    the original dictionary is preserved.

    Args:
        dct (dict): The dictionary to deserialize. Must contain at least 'class_name'
            and 'id' fields. The 'class_name' should be a fully qualified class name
            that can be loaded dynamically.

    Returns:
        OXObject: The deserialized object instance with all attributes restored.
            The returned object will have the same class type as specified in
            the 'class_name' field.

    Raises:
        OXception: If the dictionary doesn't contain the required 'class_name' field.
        OXception: If the dictionary doesn't contain the required 'id' field.

    Examples:
        >>> # Simple object deserialization
        >>> dct = {
        ...     "class_name": "base.OXObject",
        ...     "id": "12345678-1234-5678-1234-567812345678"
        ... }
        >>> obj = deserialize_from_python_dict(dct)
        >>> print(obj.class_name)
        base.OXObject
        >>> 
        >>> # Complex object with nested attributes
        >>> complex_dct = {
        ...     "class_name": "problem.OXLPProblem",
        ...     "id": "87654321-4321-8765-4321-876543218765",
        ...     "variables": [...],  # List of variable dictionaries
        ...     "constraints": [...] # List of constraint dictionaries
        ... }
        >>> problem = deserialize_from_python_dict(complex_dct)

    Note:
        The function uses a lenient approach for nested deserialization - if a nested
        dictionary cannot be deserialized (missing required fields), it is left as
        a dictionary rather than raising an exception.

    See Also:
        :func:`serialize_to_python_dict`: Reverse operation to create dictionaries.
        :func:`utilities.class_loaders.load_class`: Dynamic class loading mechanism.
    """
    if "class_name" not in dct:
        raise OXception("class_name not found in dictionary")
    if "id" not in dct:
        raise OXception("id not found in dictionary")
    class_name = dct["class_name"]
    clazz = load_class(class_name)
    retval = clazz()
    retval.id = dct["id"]
    for key, value in dct.items():
        if key != "class_name" and key != "id":
            if isinstance(value, dict):
                try:
                    value = deserialize_from_python_dict(value)
                except OXception:
                    pass
            if isinstance(value, list):
                for i in range(len(value)):
                    if isinstance(value[i], dict):
                        try:
                            value[i] = deserialize_from_python_dict(value[i])
                        except OXception:
                            pass
            setattr(retval, key, value)
    return retval
