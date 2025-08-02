"""
Base Package for OptiX Mathematical Optimization Framework
===========================================================

This package provides the foundational classes and infrastructure for the OptiX mathematical
optimization framework. It contains the core building blocks that are used throughout the
entire library to ensure consistent object identity, exception handling, and container
management across all optimization components.

The base package serves as the dependency-free foundation layer that all other OptiX
modules build upon. It provides essential functionality for object lifecycle management,
error handling with rich debugging context, and flexible container operations optimized
for optimization problem construction.

Architecture:
    - **Object Foundation**: UUID-based identity system for all optimization objects
    - **Container Management**: Flexible collection classes with search and filtering capabilities
    - **Exception Handling**: Enhanced error reporting with automatic context capture
    - **Type Safety**: Strong typing and consistent interfaces across all base classes
    - **Memory Efficiency**: Lightweight object design optimized for large-scale problems

Key Components:
    - **OXObject**: Base class providing UUID-based identity for all optimization objects
    - **OXObjectPot**: Generic container class for managing collections of optimization objects
    - **OXception**: Enhanced exception class with automatic debugging context capture

Design Principles:
    - **Minimal Dependencies**: Base package has no external dependencies beyond Python standard library
    - **Performance First**: Optimized for handling thousands of variables, constraints, and objects
    - **Debugging Support**: Rich error reporting and object introspection capabilities
    - **Extensibility**: Designed as foundation for specialized optimization object types
    - **Thread Safety**: Basic thread-safe operations for concurrent optimization scenarios

Usage:
    The base package is typically imported by higher-level OptiX modules rather than
    used directly by end users:

    .. code-block:: python

        from base import OXObject, OXObjectPot, OXception
        from dataclasses import dataclass
        
        # Create a specialized optimization object
        @dataclass
        class OptimizationVariable(OXObject):
            name: str
            lower_bound: float = 0.0
            upper_bound: float = float('inf')
            is_integer: bool = False
        
        # Use container for managing collections
        variables = OXObjectPot()
        x1 = OptimizationVariable(name="x1", upper_bound=100.0)
        x2 = OptimizationVariable(name="x2", is_integer=True)
        
        variables.add_object(x1)
        variables.add_object(x2)
        
        # Search and filter operations
        integer_vars = variables.search(is_integer=True)
        bounded_vars = variables.search_by_function(
            lambda v: v.upper_bound < float('inf')
        )
        
        # Error handling with rich context
        try:
            if x1.lower_bound > x1.upper_bound:
                raise OXception("Invalid variable bounds detected")
        except OXception as e:
            print(f"Error in {e.file_name}:{e.line_nr} - {e.message}")

Integration:
    This package integrates with other OptiX modules to provide:
    
    - **Variable Management**: Foundation for OXVariable and OXVariableSet
    - **Constraint System**: Base classes for OXConstraint and OXConstraintSet  
    - **Problem Definition**: Object identity for OXLPProblem, OXGPProblem, OXCSPProblem
    - **Data Management**: Container infrastructure for OXData and OXDatabase
    - **Solver Interface**: Object tracking for solver state and solution management

Performance Characteristics:
    - Object creation: ~50-100 microseconds per object (including UUID generation)
    - Container operations: O(1) insertion, O(n) search (linear scan)
    - Memory overhead: ~200 bytes per object (UUID + metadata)
    - Exception creation: ~1-2ms (includes stack frame analysis)

Notes:
    - All OptiX objects should inherit from OXObject for consistency
    - Use OXObjectPot as base for specialized containers (variables, constraints, etc.)
    - Prefer OXception over standard exceptions for better debugging in optimization contexts
    - Container search operations are not indexed - consider specialized containers for large collections
"""

from .OXObject import OXObject
from .OXObjectPot import OXObjectPot  
from .OXception import OXception

__all__ = [
    # Core object infrastructure
    "OXObject",
    
    # Container management
    "OXObjectPot",
    
    # Exception handling
    "OXception",
]
