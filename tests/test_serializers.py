# tests/test_serializers.py

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


