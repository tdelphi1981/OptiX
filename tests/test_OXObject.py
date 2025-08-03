"""
OptiX Base Object Test Suite
============================

This module provides comprehensive test coverage for the OXObject class,
which serves as the foundational base class for all objects in the OptiX
optimization framework. The OXObject class implements UUID-based identity,
class name tracking, and hash table compatibility.

The OXObject class provides essential functionality for object identification,
comparison, and storage across the entire OptiX ecosystem, ensuring consistent
object behavior and reliable identity management.

Example:
    Running the base object test suite:

    .. code-block:: bash

        # Run all base object tests
        poetry run python -m pytest tests/test_OXObject.py -v
        
        # Run initialization tests
        poetry run python -m pytest tests/test_OXObject.py -k "initialization" -v
        
        # Run identity and equality tests
        poetry run python -m pytest tests/test_OXObject.py -k "equality" -v

Module Dependencies:
    - uuid: For UUID generation and handling in object identity management
    - base.OXObject: Core base class providing object identity and metadata

Test Coverage:
    - Default initialization with automatic UUID generation
    - Custom ID initialization for predetermined object identities
    - String and repr representation formatting
    - Hash function implementation for dictionary and set usage
    - Equality and identity comparison based on UUID
    - Class name tracking and post-initialization setup

Base Object Features Tested:
    - UUID-based object identity with automatic generation
    - Class name tracking for object type identification
    - Hash table compatibility for efficient storage and retrieval
    - String representation for debugging and logging
    - Post-initialization setup for derived class support
    - Identity-based equality for object comparison
"""

from uuid import UUID

from base.OXObject import OXObject


def test_default_initialization():
    """Test that OXObject initializes with default values."""
    obj = OXObject()
    assert isinstance(obj.id, UUID)
    assert obj.class_name == "base.OXObject.OXObject"


def test_custom_id_initialization():
    """Test that OXObject can be initialized with a custom ID."""
    custom_id = UUID("12345678-1234-5678-1234-567812345678")
    obj = OXObject(id=custom_id)
    assert obj.id == custom_id
    assert obj.class_name == "base.OXObject.OXObject"


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
    assert obj.class_name == "base.OXObject.OXObject"
    
    # Reset class_name and call __post_init__ manually
    obj.class_name = ""
    obj.__post_init__()
    assert obj.class_name == "base.OXObject.OXObject"