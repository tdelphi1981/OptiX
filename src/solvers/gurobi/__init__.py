"""
Gurobi Solver Integration Module
================================

This module provides Gurobi commercial solver integration for the OptiX mathematical
optimization framework. It implements the Gurobi-specific solver interface that enables
high-performance optimization for linear programming, goal programming, and constraint
satisfaction problems using Gurobi's advanced optimization engine.

The module is organized around the following key components:

Architecture:
    - **Solver Interface**: Gurobi-specific implementation of OptiX solver interface
    - **Variable Translation**: Automatic conversion of OptiX variables to Gurobi format
    - **Constraint Handling**: Support for all OptiX constraint types and operators
    - **Solution Extraction**: Comprehensive solution status and value retrieval

Key Features:
    - High-performance commercial optimization engine integration
    - Support for binary, integer, and continuous variable types
    - Advanced constraint handling including goal programming
    - Configurable solver parameters and optimization settings
    - Robust solution status detection and error handling

Solver Capabilities:
    - **Linear Programming (LP)**: Standard optimization with linear constraints
    - **Goal Programming (GP)**: Multi-objective optimization with deviation variables
    - **Constraint Satisfaction (CSP)**: Feasibility problems without optimization
    - **Mixed-Integer Programming**: Support for both continuous and integer variables

Usage:
    The Gurobi solver is typically accessed through OptiX's unified solver factory:

    .. code-block:: python

        from solvers.OXSolverFactory import solve
        from problem import OXLPProblem
        
        # Create your optimization problem
        problem = OXLPProblem()
        # ... configure variables, constraints, objective ...
        
        # Solve using Gurobi
        status = solve(problem, 'Gurobi', use_continuous=True)

Requirements:
    - Gurobi optimization software and valid license
    - gurobipy Python package
    - OptiX framework core components

Notes:
    - Gurobi requires a valid license for operation
    - Performance characteristics may vary based on problem size and type
    - Advanced Gurobi parameters can be configured through solver settings
"""

from .OXGurobiSolverInterface import OXGurobiSolverInterface

__all__ = [
    # Gurobi solver interface
    "OXGurobiSolverInterface",
]