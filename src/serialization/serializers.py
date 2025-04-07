from dataclasses import asdict

from base import OXObject
from base import OXception
from utilities.class_loaders import load_class


def serialize_to_python_dict(obj: OXObject) -> dict:
    """Serialize an OXObject to a Python dictionary.

    This function converts an OXObject to a dictionary using the asdict function
    from the dataclasses module.

    Args:
        obj (OXObject): The object to serialize.

    Returns:
        dict: A dictionary representation of the object.

    Examples:
        >>> obj = OXObject()
        >>> dct = serialize_to_python_dict(obj)
        >>> print(dct["class_name"])
        base.OXObject

    See Also:
        :func:`deserialize_from_python_dict`
        :func:`dataclasses.asdict`
    """
    return asdict(obj)


def deserialize_from_python_dict(dct: dict) -> OXObject:
    """Deserialize a Python dictionary to an OXObject.

    This function converts a dictionary to an OXObject by:
    1. Loading the class using the class_name field
    2. Creating a new instance of the class
    3. Setting the id field
    4. Recursively deserializing nested dictionaries and lists of dictionaries
    5. Setting all other attributes on the object

    Args:
        dct (dict): The dictionary to deserialize.

    Returns:
        OXObject: The deserialized object.

    Raises:
        OXception: If the dictionary doesn't contain the required class_name or id fields.

    Examples:
        >>> dct = {
        ...     "class_name": "base.OXObject",
        ...     "id": "12345678-1234-5678-1234-567812345678"
        ... }
        >>> obj = deserialize_from_python_dict(dct)
        >>> print(obj.class_name)
        base.OXObject

    See Also:
        :func:`serialize_to_python_dict`
        :func:`utilities.class_loaders.load_class`
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
