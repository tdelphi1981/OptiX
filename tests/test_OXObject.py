import pytest
from uuid import UUID

from src.base.OXObject import OXObject


def test_default_initialization():
    """Test that OXObject initializes with default values."""
    obj = OXObject()
    assert isinstance(obj.id, UUID)
    assert obj.class_name == "base.OXObject"


def test_custom_id_initialization():
    """Test that OXObject can be initialized with a custom ID."""
    custom_id = UUID("12345678-1234-5678-1234-567812345678")
    obj = OXObject(id=custom_id)
    assert obj.id == custom_id
    assert obj.class_name == "base.OXObject"


def test_string_representation():
    """Test the string representation of OXObject."""
    obj = OXObject()
    str_repr = str(obj)
    assert "base.OXObject" in str_repr
    assert str(obj.id) in str_repr


def test_repr_representation():
    """Test the repr representation of OXObject."""
    obj = OXObject()
    repr_str = repr(obj)
    assert repr_str == str(obj)


def test_hash_function():
    """Test that the hash function returns the hash of the ID."""
    obj = OXObject()
    assert hash(obj) == hash(obj.id)


def test_equality_with_same_id():
    """Test that two OXObjects with the same ID are considered equal by hash tables."""
    custom_id = UUID("12345678-1234-5678-1234-567812345678")
    obj1 = OXObject(id=custom_id)
    obj2 = OXObject(id=custom_id)
    
    # Objects with same ID should have same hash
    assert hash(obj1) == hash(obj2)
    
    # Test in a dictionary
    obj_dict = {obj1: "value"}
    assert obj2 in obj_dict


def test_post_init_sets_class_name():
    """Test that __post_init__ sets the class_name attribute correctly."""
    obj = OXObject()
    assert obj.class_name == "base.OXObject"
    
    # Reset class_name and call __post_init__ manually
    obj.class_name = ""
    obj.__post_init__()
    assert obj.class_name == "base.OXObject"