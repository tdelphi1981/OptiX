"""
Problem Types Module
====================

This module provides problem type classes for representing different types of optimization 
problems in the OptiX framework. It implements a hierarchical structure supporting Constraint 
Satisfaction Problems (CSP), Linear Programming (LP), and Goal Programming (GP).

The module is organized around the following key components:

Architecture:
    - **Base Problem Types**: Hierarchical problem classes with increasing complexity
    - **Special Constraints**: Non-linear constraint types for advanced modeling
    - **Objective Types**: Support for minimization and maximization objectives  
    - **Progressive Complexity**: Each problem type builds upon the previous one

Key Features:
    - Constraint Satisfaction Problems (CSP) with variables and constraints
    - Linear Programming (LP) with objective function optimization
    - Goal Programming (GP) with multi-objective goal constraints and deviation variables
    - Special constraint types for non-linear operations (multiplication, division, modulo, conditional)
    - Flexible variable creation from database objects using Cartesian products
    - Template-based variable naming and description generation

Problem Types Covered:
    - **OXCSPProblem**: Base constraint satisfaction problems with variables and constraints
    - **OXLPProblem**: Linear programming problems extending CSP with objective functions
    - **OXGPProblem**: Goal programming problems extending LP with goal constraints
    - **SpecialConstraintType**: Enumeration of special constraint types for non-linear operations
    - **ObjectiveType**: Enumeration of objective types (minimize/maximize)

Usage:
    Import specific problem classes for the optimization tasks you need:

    .. code-block:: python

        from problem import OXLPProblem, OXGPProblem, ObjectiveType
        from constraints import RelationalOperators
        
        # Create and configure a linear programming problem
        lp_problem = OXLPProblem()
        lp_problem.create_decision_variable("x", lower_bound=0, upper_bound=10)
        lp_problem.create_decision_variable("y", lower_bound=0, upper_bound=10)
        
        # Add constraint: x + y <= 15
        lp_problem.create_constraint(
            variables=[lp_problem.variables[0].id, lp_problem.variables[1].id],
            weights=[1, 1],
            operator=RelationalOperators.LESS_THAN_EQUAL,
            value=15
        )
        
        # Set objective: maximize 3x + 2y
        lp_problem.create_objective_function(
            variables=[lp_problem.variables[0].id, lp_problem.variables[1].id],
            weights=[3, 2],
            objective_type=ObjectiveType.MAXIMIZE
        )

Notes:
    - All problem types support integration with database objects for variable creation
    - Special constraints enable modeling of non-linear relationships
    - Goal programming allows handling of multiple conflicting objectives
    - Follow the progressive complexity pattern when choosing problem types
    - Ensure proper constraint and variable relationships in problem formulation
"""

from .OXProblem import (
    OXCSPProblem,
    OXLPProblem,
    OXGPProblem,
    SpecialConstraintType,
    ObjectiveType
)

__all__ = [
    # Problem type classes
    "OXCSPProblem",
    "OXLPProblem", 
    "OXGPProblem",
    
    # Enumerations
    "SpecialConstraintType",
    "ObjectiveType",
]