"""
Variables Module
================

This module provides comprehensive decision variable management for the OptiX 
optimization framework. It implements a complete variable system supporting 
linear programming (LP), goal programming (GP), and constraint satisfaction 
problems (CSP) with advanced features for bounds management, relationship tracking, 
and specialized variable types.

The module is organized around a hierarchical variable architecture that extends
from basic decision variables to specialized types for complex optimization scenarios,
providing type-safe operations and efficient collection management capabilities.

Architecture:
    - **Base Variables**: Core OXVariable class with bounds, values, and relationship tracking
    - **Specialized Variables**: Goal programming deviation variables with desirability flags
    - **Collection Management**: Type-safe containers for variable organization and querying
    - **Relationship System**: UUID-based linking for complex data modeling scenarios

Key Components:
    - **OXVariable**: Fundamental decision variable with bounds and relationship tracking
    - **OXDeviationVar**: Specialized variables for goal programming with deviation semantics
    - **OXVariableSet**: Type-safe container with relationship-based querying capabilities
    - **Validation System**: Comprehensive bounds checking and type enforcement

Core Features:
    - Automatic bounds validation with infinity support for unbounded variables
    - UUID-based relationship tracking for linking variables to business entities
    - Type-safe collection operations with strict variable type enforcement
    - Advanced querying capabilities based on variable relationships and attributes
    - Goal programming support with deviation direction and desirability tracking

Variable Types:
    - **Decision Variables**: Standard optimization variables with bounds and values
    - **Deviation Variables**: Goal programming variables for measuring target deviations
    - **Container Variables**: Collections providing organization and querying capabilities
    - **Relationship Variables**: Variables linked to business entities through UUID references

Use Cases:
    - Linear programming models with continuous and discrete decision variables
    - Goal programming problems with multiple objectives and deviation measurements
    - Multi-objective optimization with priority-based goal hierarchies
    - Resource allocation problems with complex business entity relationships
    - Production planning with capacity constraints and quality targets

Usage:
    Import variable classes for optimization model construction:

    .. code-block:: python

        from variables import OXVariable, OXVariableSet, OXDeviationVar
        from uuid import uuid4
        
        # Create decision variables for production planning
        production_var = OXVariable(
            name="daily_production",
            description="Daily production quantity",
            lower_bound=0,
            upper_bound=1000,
            value=500
        )
        
        # Create deviation variables for goal programming
        budget_overrun = OXDeviationVar(
            name="budget_deviation_positive",
            description="Amount over budget",
            lower_bound=0,
            desired=False  # Minimize over-spending
        )
        
        # Organize variables in type-safe collections
        var_set = OXVariableSet()
        var_set.add_object(production_var)
        var_set.add_object(budget_overrun)
        
        # Link variables to business entities
        facility_id = uuid4()
        production_var.related_data["facility"] = facility_id
        
        # Query variables by relationships
        facility_vars = var_set.query(facility=facility_id)

Performance Considerations:
    - Variable creation is optimized for large-scale problems with minimal overhead
    - Collection operations use efficient data structures for variable management
    - Relationship querying performs linear scans suitable for moderate-sized collections
    - Memory usage is minimized through efficient storage of variable references

Notes:
    - All variable operations include comprehensive validation and error handling
    - Bounds checking ensures mathematical consistency throughout optimization workflows
    - Type safety is enforced at runtime to prevent optimization model corruption
    - Variables integrate seamlessly with constraint and solver components

See Also:
    :mod:`base`: Base classes and exceptions used by variable implementations.
    :mod:`constraints`: Constraint classes that utilize variables in mathematical expressions.
    :mod:`solvers`: Solver interfaces that process variables for optimization execution.
"""

from .OXDeviationVar import OXDeviationVar
from .OXVariable import OXVariable
from .OXVariableSet import OXVariableSet

__all__ = [
    # Core decision variables
    "OXVariable",
    
    # Variable collections and containers
    "OXVariableSet",
    
    # Specialized variables for goal programming
    "OXDeviationVar",
]