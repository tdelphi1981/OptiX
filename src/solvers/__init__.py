"""Solvers package for the OptiX optimization framework.

This package provides a unified interface for various optimization solvers
and serves as the main entry point for solving optimization problems.
The package includes solver interfaces, factory methods, and solver-specific
implementations.

Modules:
    OXSolverFactory: Factory module for creating and managing solver instances.
    OXSolverInterface: Abstract base class and common data structures for all solvers.
    ortools: Subpackage containing OR-Tools specific solver implementations.

The main entry point for solving problems is the `solve` function from
OXSolverFactory, which provides a unified interface across all solver types.

Example:
    Basic usage of the solvers package:
    
    >>> from solvers import solve
    >>> from problem.OXProblem import OXCSPProblem
    >>> 
    >>> # Create a problem instance
    >>> problem = OXCSPProblem()
    >>> # ... configure problem variables and constraints ...
    >>> 
    >>> # Solve using OR-Tools solver
    >>> status, solver = solve(problem, 'ORTools')
    >>> 
    >>> # Access solution
    >>> if len(solver) > 0:
    ...     solution = solver[0]
    ...     print(f"Solution status: {solution.status}")
    ...     print(f"Variable values: {solution.decision_variable_values}")

Available Solvers:
    - ORTools: Google's OR-Tools CP-SAT solver for constraint satisfaction 
      and linear programming problems.

Note:
    This package is designed to be extensible. New solver implementations
    should inherit from OXSolverInterface and be registered in the
    OXSolverFactory._available_solvers dictionary.
"""

# Import main solving function for convenience
from .OXSolverFactory import solve
from .OXSolverInterface import OXSolverInterface, OXSolverSolution, OXSolutionStatus

__all__ = [
    'solve',
    'OXSolverInterface', 
    'OXSolverSolution',
    'OXSolutionStatus'
]