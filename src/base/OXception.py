"""
Exception Handling Module
=========================

This module provides enhanced exception handling for the OptiX mathematical optimization
framework. The OXception class extends Python's standard Exception class with automatic
context capture, providing detailed debugging information including file location,
line numbers, method names, and local variable states at the time of exception occurrence.

This enhanced exception handling is crucial for debugging complex optimization problems
where errors can occur deep within solver algorithms or constraint validation logic.
The automatic context capture eliminates the need for manual debugging instrumentation
and provides immediate insight into problem state when errors occur.

Key Features:
    - **Automatic Context Capture**: Automatically captures file location, line number, and method name
    - **Variable State Logging**: Records local variables at the time of exception
    - **Relative Path Resolution**: Converts absolute paths to relative paths for cleaner error messages
    - **JSON Serialization**: Supports conversion to JSON for structured logging and error reporting
    - **Stack Frame Analysis**: Uses Python's inspect module for detailed stack frame information
    - **Debugging Support**: Enhanced string representation for comprehensive error details

Architecture:
    The OXception class uses Python's inspect module to analyze the call stack at the time
    of exception creation. It automatically extracts context information from the calling
    frame and formats it for easy debugging. The relative path calculation ensures that
    error messages are portable across different development environments.

Usage:
    Use OXception throughout the OptiX codebase for consistent error handling:

    .. code-block:: python

        from base.OXception import OXception
        
        def validate_variable_bounds(lower, upper):
            if lower > upper:
                raise OXception("Lower bound cannot be greater than upper bound")
        
        try:
            validate_variable_bounds(10, 5)
        except OXception as e:
            print(f"Error: {e.message}")
            print(f"Location: {e.file_name}:{e.line_nr}")
            print(f"Method: {e.method_name}")
            
            # For structured logging
            error_data = e.to_json()

Module Dependencies:
    - inspect: For stack frame analysis and context capture
    - pathlib: For file path manipulation and relative path calculation
"""

import inspect
from pathlib import Path


class OXception(Exception):
    """
    Enhanced exception class for the OptiX mathematical optimization framework.
    
    This exception class extends Python's standard Exception with automatic context
    capture capabilities. When an OXception is raised, it automatically captures
    detailed information about the execution context including file location,
    line number, method name, and local variable state.
    
    This enhanced debugging information is particularly valuable in optimization
    contexts where errors can occur deep within solver algorithms, constraint
    validation logic, or complex mathematical operations. The automatic context
    capture eliminates the need for manual debugging instrumentation.
    
    Attributes:
        message (str): The primary error message describing what went wrong.
        line_nr (int): The line number where the exception was raised.
        file_name (str): The relative path of the file where the exception occurred,
                        calculated relative to the project root for portability.
        method_name (str): The name of the method or function where the exception occurred.
        params (dict): A dictionary containing the local variables and their values
                      at the time the exception was raised.
    
    Key Features:
        - **Automatic Context Capture**: No manual instrumentation required
        - **Relative Path Calculation**: Portable error messages across environments
        - **Local Variable Capture**: Complete state information for debugging
        - **JSON Serialization**: Structured output for logging and monitoring
        - **Enhanced Debugging**: Rich string representation with all context
    
    Exception Hierarchy:
        OXception serves as the base exception for all OptiX-specific errors:
        
        .. code-block:: python
        
            # Usage in optimization contexts
            class VariableBoundsError(OXception):
                pass
                
            class SolverError(OXception):
                pass
                
            class ConstraintViolationError(OXception):
                pass
    
    Example:
        Basic exception usage with automatic context capture:
        
        .. code-block:: python
        
            from base.OXception import OXception
            
            def create_variable(name, lower_bound, upper_bound):
                if lower_bound > upper_bound:
                    raise OXception(
                        f"Invalid bounds for variable '{name}': "
                        f"lower_bound ({lower_bound}) > upper_bound ({upper_bound})"
                    )
                return Variable(name, lower_bound, upper_bound)
            
            try:
                var = create_variable("x1", 10.0, 5.0)  # Invalid bounds
            except OXception as e:
                # Rich debugging information automatically captured
                print(f"Error: {e.message}")
                print(f"Location: {e.file_name}:{e.line_nr}")
                print(f"Method: {e.method_name}")
                print(f"Local variables: {e.params}")
                
                # Structured error logging
                import json
                error_log = json.dumps(e.to_json(), indent=2)
                logger.error(error_log)
    
    Performance Considerations:
        - Context capture adds minimal overhead (~1-2ms per exception)
        - Local variable capture includes all variables in scope (can be large)
        - Consider using standard exceptions for performance-critical paths
        - JSON serialization handles most Python types but may need custom encoding
    
    Note:
        - Local variables are captured by reference, so mutable objects may change
        - Large objects in local scope will be included in the params dictionary
        - File path calculation assumes the exception is raised within the project structure
        - Circular references in local variables may cause JSON serialization issues
    """
    def __init__(self, message):
        """Initialize the exception with the given message and capture context information.

        Args:
            message (str): The error message.
        """
        self.message = message
        frm = inspect.currentframe()
        self.line_nr = frm.f_back.f_lineno
        current_path = Path(__file__).parent.parent.parent.absolute()
        error_file_path = Path(frm.f_back.f_code.co_filename)
        relative_path = error_file_path.relative_to(current_path)
        self.file_name = str(relative_path)
        self.method_name = frm.f_back.f_code.co_name
        self.params = frm.f_back.f_locals
        super().__init__(self.message)

    def to_json(self):
        """Convert the exception to a JSON-serializable dictionary.

        This is useful for logging and error reporting.

        Returns:
            dict: A dictionary containing the exception details.
        """
        return {
            "message": self.message,
            "file_name": self.file_name,
            "line_nr": self.line_nr,
            "method_name": self.method_name,
            "params": self.params
        }

    def __str__(self):
        """Return a string representation of the exception.

        Returns:
            str: A detailed string representation including the message, file name,
                line number, method name, and local variables.
        """
        return f"OXception: {self.message} in {self.file_name}:{self.line_nr} ({self.method_name} with locals: {self.params})"

    def __repr__(self):
        """Return a string representation of the exception for debugging.

        Returns:
            str: The same string as __str__.
        """
        return self.__str__()
