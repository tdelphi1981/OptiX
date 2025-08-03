"""
OptiX Serialization System Test Suite
=====================================

This module provides comprehensive test coverage for the serialization and
deserialization system in the OptiX optimization framework. The serialization
system enables persistent storage, data exchange, and object reconstruction
for all OptiX objects and complex data structures.

The serialization system supports conversion between OptiX objects and Python
dictionaries, enabling JSON serialization, database storage, and inter-process
communication while preserving object identity and relationships.

Example:
    Running the serialization test suite:

    .. code-block:: bash

        # Run all serialization tests
        poetry run python -m pytest tests/test_serializers.py -v
        
        # Run serialization tests
        poetry run python -m pytest tests/test_serializers.py -k "serialize" -v
        
        # Run deserialization tests
        poetry run python -m pytest tests/test_serializers.py -k "deserialize" -v

Module Dependencies:
    - pytest: Testing framework for assertion handling and exception testing
    - base.OXObject: Base object class for serialization testing
    - base.OXObjectPot: Container class for collection serialization
    - base.OXception: Custom exception handling for serialization errors
    - serialization.serializers: Core serialization and deserialization functions

Test Coverage:
    - Object serialization to Python dictionaries
    - Container serialization with nested objects
    - Unique identifier preservation during serialization
    - Object deserialization from dictionary representations
    - Error handling for invalid or missing class information
    - Round-trip serialization/deserialization validation

Serialization Features Tested:
    - OXObject serialization with ID and class name preservation
    - OXObjectPot serialization with nested object handling
    - Unique identifier generation and validation
    - Dictionary-based object reconstruction
    - Class name validation and dynamic loading
    - Error handling for malformed serialization data
"""

import pytest

from base import OXObject
from base import OXObjectPot
from base import OXception
from serialization.serializers import serialize_to_python_dict, deserialize_from_python_dict


def test_serialize_to_python_dict_valid_oxobject():
    obj = OXObject()
    result = serialize_to_python_dict(obj)
    assert isinstance(result, dict)
    assert result["id"] == obj.id
    assert result["class_name"] == obj.class_name

def test_serialize_to_python_dict_oxobject_pot():
    obj = OXObjectPot()
    obj.add_object(OXObject())
    obj.add_object(OXObject())
    result = serialize_to_python_dict(obj)
    assert isinstance(result, dict)
    assert len(result["objects"]) == 2



def test_serialize_to_python_dict_unique_id():
    obj1 = OXObject()
    obj2 = OXObject()
    result1 = serialize_to_python_dict(obj1)
    result2 = serialize_to_python_dict(obj2)
    assert result1["id"] != result2["id"]


def test_deserialize_from_python_dict_valid_input():
    data = {"id": "6f95d2fa-1b85-4ea0-a9f0-810de28633b3", "class_name": "base.OXObject.OXObject"}
    obj = deserialize_from_python_dict(data)
    assert isinstance(obj, OXObject)
    assert str(obj.id) == data["id"]
    assert obj.class_name == data["class_name"]


def test_deserialize_from_python_dict_missing_class_name():
    data = {"id": "6f95d2fa-1b85-4ea0-a9f0-810de28633b3"}
    with pytest.raises(OXception):
        deserialize_from_python_dict(data)


def test_deserialize_from_python_dict_invalid_class():
    data = {"id": "6f95d2fa-1b85-4ea0-a9f0-810de28633b3", "class_name": "nonexistent.ClassName"}
    with pytest.raises(OXception):
        deserialize_from_python_dict(data)


def test_deserialize_from_python_dict_nested_object():
    nested_data = {"id": "11111111-1111-1111-1111-111111111111", "class_name": "base.OXObject.OXObject"}
    data = {
        "id": "6f95d2fa-1b85-4ea0-a9f0-810de28633b3",
        "class_name": "base.OXObjectPot.OXObjectPot",
        "objects": [nested_data]
    }
    obj = deserialize_from_python_dict(data)
    assert isinstance(obj, OXObjectPot)
    assert len(obj.objects) == 1
    assert isinstance(obj.objects[0], OXObject)
    assert str(obj.objects[0].id) == nested_data["id"]


