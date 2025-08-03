"""OR-Tools solver implementation subpackage.

This subpackage contains the OR-Tools specific implementation of the
OptiX solver interface. It provides integration with Google's OR-Tools
CP-SAT solver for solving constraint satisfaction and linear programming
problems.

Modules:
    OXORToolsSolverInterface: Main solver implementation using OR-Tools CP-SAT.

The OR-Tools solver supports:
    - Boolean and integer decision variables
    - Linear constraints with various relational operators
    - Special constraints (multiplication, division, modulo, summation, conditional)
    - Objective functions for optimization problems
    - Multiple solution enumeration
    - Time limits and solution count limits

Features:
    - Automatic handling of boolean variables (0-1 bounds)
    - Integer variable support with custom bounds
    - Float weight handling through denominator equalization
    - Special constraint types for complex mathematical operations
    - Conditional constraints for if-then-else logic
    - Solution callback mechanism for collecting multiple solutions

Parameters:
    The OR-Tools solver supports the following parameters:
    
    - equalizeDenominators (bool): Enable denominator equalization for float weights.
      When True, float weights are converted to integers by finding common denominators.
      Default: False
      
    - solutionCount (int): Maximum number of solutions to collect.
      Default: 1
      
    - maxTime (int): Maximum solving time in seconds.
      Default: 600 (10 minutes)

Example:
    Using the OR-Tools solver with custom parameters:
    
    >>> from solvers.ortools import OXORToolsSolverInterface
    >>> from problem.OXProblem import OXCSPProblem
    >>> 
    >>> # Create problem
    >>> problem = OXCSPProblem()
    >>> # ... configure problem ...
    >>> 
    >>> # Create solver with custom parameters
    >>> solver = OXORToolsSolverInterface(
    ...     equalizeDenominators=True,
    ...     solutionCount=5,
    ...     maxTime=300
    ... )
    >>> 
    >>> # Solve
    >>> solver.create_variable(problem)
    >>> solver.create_constraints(problem)
    >>> solver.create_special_constraints(problem)
    >>> status = solver.solve(problem)
    >>> 
    >>> # Access solutions
    >>> for solution in solver:
    ...     print(f"Solution: {solution.decision_variable_values}")

Requirements:
    - ortools: Google's OR-Tools optimization library
    - Python 3.7+

Note:
    This implementation uses OR-Tools' CP-SAT solver, which is particularly
    well-suited for constraint satisfaction problems and integer programming.
    For continuous optimization problems, consider using other solvers.
"""

from .OXORToolsSolverInterface import OXORToolsSolverInterface

__all__ = ['OXORToolsSolverInterface']