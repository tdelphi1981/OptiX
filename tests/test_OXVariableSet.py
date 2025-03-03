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
