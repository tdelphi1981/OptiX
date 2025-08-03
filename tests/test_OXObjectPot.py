"""
OptiX Object Container Test Suite
=================================

This module provides comprehensive test coverage for the OXObjectPot class,
which implements a container for managing collections of OXObject instances
in the OptiX optimization framework. The OXObjectPot serves as a specialized
collection that provides object storage, retrieval, and manipulation capabilities.

The OXObjectPot class is essential for managing groups of related objects
such as variables, constraints, or data elements within optimization problems,
providing efficient access patterns and collection operations.

Example:
    Running the object container test suite:

    .. code-block:: bash

        # Run all object pot tests
        poetry run python -m pytest tests/test_OXObjectPot.py -v
        
        # Run object manipulation tests
        poetry run python -m pytest tests/test_OXObjectPot.py -k "add_object" -v
        
        # Run search and retrieval tests
        poetry run python -m pytest tests/test_OXObjectPot.py -k "search" -v

Module Dependencies:
    - pytest: Testing framework for assertion handling and test execution
    - src.base.OXObject: Base object class for container element type
    - src.base.OXObjectPot: Container class for managing object collections

Test Coverage:
    - Default initialization and empty state validation
    - Object addition and removal operations
    - Collection length and membership testing
    - Object retrieval by index and search criteria
    - Iterator protocol implementation
    - Last object access for recent additions
    - Collection clearing and state reset

Container Operations Tested:
    - Object addition with automatic indexing
    - Object removal with list maintenance
    - Search functionality for finding specific objects
    - Index-based access for direct object retrieval
    - Length calculation for collection size
    - Iterator support for collection traversal
"""

import pytest

from src.base.OXObject import OXObject
from src.base.OXObjectPot import OXObjectPot


class TestObject(OXObject):
    """A simple test object class for testing OXObjectPot."""
    def __init__(self, name=None, value=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.value = value


def test_default_initialization():
    """Test that OXObjectPot initializes with an empty list of objects."""
    pot = OXObjectPot()
    assert isinstance(pot.objects, list)
    assert len(pot.objects) == 0
    assert len(pot) == 0


def test_add_object():
    """Test adding objects to the pot."""
    pot = OXObjectPot()
    obj1 = TestObject(name="obj1", value=1)
    obj2 = TestObject(name="obj2", value=2)
    
    pot.add_object(obj1)
    assert len(pot) == 1
    assert pot.objects[0] == obj1
    
    pot.add_object(obj2)
    assert len(pot) == 2
    assert pot.objects[1] == obj2


def test_remove_object():
    """Test removing objects from the pot."""
    pot = OXObjectPot()
    obj1 = TestObject(name="obj1", value=1)
    obj2 = TestObject(name="obj2", value=2)
    
    pot.add_object(obj1)
    pot.add_object(obj2)
    assert len(pot) == 2
    
    pot.remove_object(obj1)
    assert len(pot) == 1
    assert obj1 not in pot.objects
    assert obj2 in pot.objects
    
    # Test removing an object that's not in the pot
    with pytest.raises(ValueError):
        pot.remove_object(obj1)


def test_iteration():
    """Test iterating over objects in the pot."""
    pot = OXObjectPot()
    obj1 = TestObject(name="obj1", value=1)
    obj2 = TestObject(name="obj2", value=2)
    
    pot.add_object(obj1)
    pot.add_object(obj2)
    
    objects = list(pot)
    assert len(objects) == 2
    assert obj1 in objects
    assert obj2 in objects


def test_search():
    """Test searching for objects with matching attributes."""
    pot = OXObjectPot()
    obj1 = TestObject(name="obj1", value=1)
    obj2 = TestObject(name="obj2", value=2)
    obj3 = TestObject(name="obj3", value=1)
    
    pot.add_object(obj1)
    pot.add_object(obj2)
    pot.add_object(obj3)
    
    # Search by name
    results = pot.search(name="obj1")
    assert len(results) == 1
    assert results[0] == obj1
    
    # Search by value
    results = pot.search(value=1)
    assert len(results) == 2
    assert obj1 in results
    assert obj3 in results
    
    # Search with multiple criteria
    results = pot.search(name="obj3", value=1)
    assert len(results) == 1
    assert results[0] == obj3
    
    # Search with no matches
    results = pot.search(name="nonexistent")
    assert len(results) == 0


def test_search_by_function():
    """Test searching for objects using a predicate function."""
    pot = OXObjectPot()
    obj1 = TestObject(name="obj1", value=1)
    obj2 = TestObject(name="obj2", value=2)
    obj3 = TestObject(name="obj3", value=3)
    
    pot.add_object(obj1)
    pot.add_object(obj2)
    pot.add_object(obj3)
    
    # Search for objects with even values
    results = pot.search_by_function(lambda obj: obj.value % 2 == 0)
    assert len(results) == 1
    assert results[0] == obj2
    
    # Search for objects with names containing "obj"
    results = pot.search_by_function(lambda obj: "obj" in obj.name)
    assert len(results) == 3
    
    # Search with no matches
    results = pot.search_by_function(lambda obj: obj.value > 10)
    assert len(results) == 0


def test_first_last_object_properties():
    """Test the first_object and last_object properties."""
    pot = OXObjectPot()
    obj1 = TestObject(name="obj1", value=1)
    obj2 = TestObject(name="obj2", value=2)
    
    pot.add_object(obj1)
    assert pot.first_object == obj1
    assert pot.last_object == obj1
    
    pot.add_object(obj2)
    assert pot.first_object == obj1
    assert pot.last_object == obj2
    
    # Test with empty pot
    empty_pot = OXObjectPot()
    with pytest.raises(IndexError):
        _ = empty_pot.first_object
    with pytest.raises(IndexError):
        _ = empty_pot.last_object


def test_get_object_types():
    """Test getting the types of objects in the pot."""
    pot = OXObjectPot()
    obj1 = TestObject(name="obj1", value=1)
    obj2 = OXObject()
    
    pot.add_object(obj1)
    pot.add_object(obj2)
    
    types = pot.get_object_types()
    assert len(types) == 2
    assert "testobject" in types
    assert "object" in types