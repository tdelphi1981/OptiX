"""
OptiX Variable Set Test Suite
=============================

This module provides comprehensive test coverage for the OXVariableSet class,
which implements a specialized container for managing collections of OXVariable
instances in the OptiX optimization framework. The OXVariableSet extends the
base OXObjectPot functionality with variable-specific operations and validation.

The OXVariableSet class provides type-safe variable storage, query capabilities
based on variable metadata, and ensures that only valid OXVariable instances
can be added to the collection.

Example:
    Running the variable set test suite:

    .. code-block:: bash

        # Run all variable set tests
        poetry run python -m pytest tests/test_OXVariableSet.py -v
        
        # Run variable addition/removal tests
        poetry run python -m pytest tests/test_OXVariableSet.py -k "add_object or remove_object" -v
        
        # Run query functionality tests
        poetry run python -m pytest tests/test_OXVariableSet.py -k "query" -v

Module Dependencies:
    - uuid: For generating unique identifiers in variable metadata
    - pytest: Testing framework for assertion handling and exception testing
    - base.OXObject: Base object class for type validation testing
    - base.OXception: Custom exception handling for invalid operations
    - variables.OXVariable: Variable class for container elements
    - variables.OXVariableSet: Specialized variable container implementation

Test Coverage:
    - Type-safe object addition with OXVariable validation
    - Invalid object rejection with appropriate exception handling
    - Object removal with type checking and validation
    - Query functionality based on variable metadata and properties
    - Collection membership testing and size validation
    - Variable retrieval by various search criteria

Variable Set Operations Tested:
    - Valid variable addition to the set
    - Invalid object rejection with OXception
    - Variable removal with type validation
    - Metadata-based querying and filtering
    - Collection size and membership operations
    - Search functionality for variable discovery
"""

from uuid import uuid4

import pytest

from base import OXObject
from base.OXception import OXception
from variables.OXVariable import (OXVariable)
from variables.OXVariableSet import OXVariableSet


def test_add_object_valid():
    variable_set = OXVariableSet()
    variable = OXVariable(name="test_var")
    variable_set.add_object(variable)
    assert len(variable_set) == 1
    assert variable in variable_set


def test_add_object_invalid():
    variable_set = OXVariableSet()
    with pytest.raises(OXception, match="Only OXVariable can be added to OXVariableSet"):
        variable_set.add_object(OXObject())


def test_remove_object_valid():
    variable_set = OXVariableSet()
    variable = OXVariable(name="test_var")
    variable_set.add_object(variable)
    assert len(variable_set) == 1
    variable_set.remove_object(variable)
    assert len(variable_set) == 0


def test_remove_object_invalid():
    variable_set = OXVariableSet()
    with pytest.raises(OXception, match="Only OXVariable can be removed from OXVariableSet"):
        variable_set.remove_object(OXObject())


def test_query_matching_variable():
    variable_set = OXVariableSet()
    variable1 = OXVariable(name="test_var1", related_data={"key1": uuid4()})
    variable2 = OXVariable(name="test_var2", related_data={"key2": uuid4()})
    variable_set.add_object(variable1)
    variable_set.add_object(variable2)
    result = variable_set.query(key1=variable1.related_data["key1"])
    assert len(result) == 1
    assert variable1 in result


def test_query_no_match():
    variable_set = OXVariableSet()
    variable1 = OXVariable(name="test_var1", related_data={"key1": uuid4()})
    variable2 = OXVariable(name="test_var2", related_data={"key2": uuid4()})
    variable_set.add_object(variable1)
    variable_set.add_object(variable2)
    result = variable_set.query(key3=uuid4())
    assert len(result) == 0


def test_query_empty_variable_set():
    variable_set = OXVariableSet()
    result = variable_set.query(key1=uuid4())
    assert len(result) == 0
