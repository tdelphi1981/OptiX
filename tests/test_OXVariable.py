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
