"""
OptiX Exception Handling Test Suite
===================================

This module provides comprehensive test coverage for the OXception class,
which implements enhanced exception handling for the OptiX optimization
framework. The OXception class extends standard Python exceptions with
context information capture, debugging support, and structured error reporting.

The OXception class automatically captures execution context including
file names, line numbers, method names, and parameter information to
facilitate debugging and error analysis in complex optimization workflows.

Example:
    Running the exception handling test suite:

    .. code-block:: bash

        # Run all exception tests
        poetry run python -m pytest tests/test_OXception.py -v
        
        # Run context capture tests
        poetry run python -m pytest tests/test_OXception.py -k "initialization" -v
        
        # Run serialization tests
        poetry run python -m pytest tests/test_OXception.py -k "json" -v

Module Dependencies:
    - src.base.OXception: Enhanced exception class with context capture

Test Coverage:
    - Exception initialization with message and context capture
    - Automatic file name, line number, and method name extraction
    - Parameter dictionary creation for debugging information
    - String and repr representation formatting
    - JSON serialization for error logging and reporting
    - Context information accuracy and relative path handling

Exception Features Tested:
    - Message storage and retrieval
    - Context information capture (file, line, method)
    - Parameter dictionary for debugging data
    - String representation for error display
    - JSON serialization for structured error reporting
    - Relative path calculation for file references
"""

from src.base.OXception import OXception


def test_initialization():
    """Test that OXception initializes with the correct message and captures context information."""
    try:
        # Raise an OXception with a test message
        raise OXception("Test error message")
    except OXception as e:
        # Check that the message is set correctly
        assert e.message == "Test error message"
        
        # Check that context information is captured
        assert isinstance(e.line_nr, int)
        assert isinstance(e.file_name, str)
        assert e.method_name == "test_initialization"
        assert isinstance(e.params, dict)
        
        # Check that the file name is relative to the project root
        assert not e.file_name.startswith("/")
        assert "tests/test_OXception.py" in e.file_name


def test_string_representation():
    """Test the string representation of OXception."""
    try:
        raise OXception("Test error message")
    except OXception as e:
        str_repr = str(e)
        
        # Check that the string representation includes all relevant information
        assert "OXception: Test error message" in str_repr
        assert e.file_name in str_repr
        assert str(e.line_nr) in str_repr
        assert e.method_name in str_repr


def test_repr_representation():
    """Test the repr representation of OXception."""
    try:
        raise OXception("Test error message")
    except OXception as e:
        repr_str = repr(e)
        assert repr_str == str(e)


def test_to_json():
    """Test the to_json method of OXception."""
    try:
        raise OXception("Test error message")
    except OXception as e:
        json_data = e.to_json()
        
        # Check that the JSON data includes all expected fields
        assert json_data["message"] == "Test error message"
        assert json_data["file_name"] == e.file_name
        assert json_data["line_nr"] == e.line_nr
        assert json_data["method_name"] == e.method_name
        assert json_data["params"] == e.params


def test_nested_exception():
    """Test that OXception correctly captures context when raised from a nested function."""
    def nested_function():
        raise OXception("Nested error message")
    
    try:
        nested_function()
    except OXception as e:
        # Check that the context information points to the nested function
        assert e.message == "Nested error message"
        assert e.method_name == "nested_function"


def test_exception_inheritance():
    """Test that OXception inherits from Exception."""
    try:
        raise OXception("Test error message")
    except Exception as e:
        # Check that OXception is an instance of Exception
        assert isinstance(e, Exception)
        assert isinstance(e, OXception)


def test_exception_with_locals():
    """Test that OXception captures local variables."""
    try:
        local_var1 = "test value"
        local_var2 = 42
        raise OXception("Test error message")
    except OXception as e:
        # Check that local variables are captured in params
        assert "local_var1" in e.params
        assert e.params["local_var1"] == "test value"
        assert "local_var2" in e.params
        assert e.params["local_var2"] == 42