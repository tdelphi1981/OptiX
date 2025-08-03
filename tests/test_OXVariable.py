"""
OptiX Variable Class Test Suite
===============================

This module provides comprehensive test coverage for the OXVariable class,
which represents decision variables in mathematical optimization problems.
The OXVariable class is a fundamental component of the OptiX framework,
encapsulating variable properties, bounds, metadata, and relationships.

The test suite validates variable initialization, naming conventions, bounds
handling, and metadata management to ensure robust variable creation and
manipulation throughout the optimization process.

Example:
    Running the variable test suite:

    .. code-block:: bash

        # Run all variable tests
        poetry run python -m pytest tests/test_OXVariable.py -v
        
        # Run specific initialization tests
        poetry run python -m pytest tests/test_OXVariable.py -k "initialization" -v
        
        # Run bounds-related tests
        poetry run python -m pytest tests/test_OXVariable.py -k "bounds" -v

Module Dependencies:
    - uuid: For UUID generation and handling in variable relationships
    - pytest: Testing framework for assertions and test execution
    - src.variables.OXVariable: Core variable class implementation

Test Coverage:
    - Default initialization with automatic naming and default bounds
    - Custom initialization with user-defined properties and metadata
    - Automatic name generation when empty names are provided
    - Upper and lower bound validation and assignment
    - Related data dictionary handling for variable relationships
    - Variable metadata management and retrieval

Variable Properties Tested:
    - name: Variable identifier with automatic generation fallback
    - description: Human-readable variable description
    - value: Current variable value assignment
    - upper_bound: Maximum allowable variable value
    - lower_bound: Minimum allowable variable value
    - related_data: Dictionary for storing variable relationships and metadata
"""

from uuid import UUID

import pytest

from src.variables.OXVariable import OXVariable


def test_default_initialization():
    # Test default initialization of the OXVariable class
    ox_var = OXVariable()
    assert ox_var.name.startswith("var_")
    assert isinstance(ox_var.name, str)
    assert ox_var.description == ""
    assert ox_var.value is None
    assert ox_var.upper_bound == pytest.approx(float('inf'))
    assert ox_var.lower_bound == 0
    assert isinstance(ox_var.related_data, dict)


def test_custom_initialization():
    # Test custom initialization
    ox_var = OXVariable(
        name="temperature",
        description="Temperature control variable",
        value=25.5,
        upper_bound=100,
        lower_bound=0,
        related_data={"sensor_id": UUID("12345678-1234-5678-1234-567812345678")},
    )
    assert ox_var.name == "temperature"
    assert ox_var.description == "Temperature control variable"
    assert ox_var.value == 25.5
    assert ox_var.upper_bound == 100
    assert ox_var.lower_bound == 0
    assert ox_var.related_data == {"sensor_id": UUID("12345678-1234-5678-1234-567812345678")}


def test_empty_name_defaults_to_id():
    # Test that an empty name defaults to a name based on the ID
    ox_var = OXVariable(name="")
    assert ox_var.name.startswith("var_")
    assert len(ox_var.name) > 4  # Account for the "var_" prefix


def test_bounds_check():
    # Test if bounds are properly handled
    ox_var = OXVariable(upper_bound=50, lower_bound=10)
    assert ox_var.upper_bound == 50
    assert ox_var.lower_bound == 10


def test_related_data_defaults_to_empty_dict():
    # Test that related_data defaults to an empty dict
    ox_var = OXVariable()
    assert isinstance(ox_var.related_data, dict)
    assert len(ox_var.related_data) == 0
