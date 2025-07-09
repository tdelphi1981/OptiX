"""Problem package for the OptiX optimization framework.

This package contains classes for representing different types of optimization problems.
It provides a hierarchical structure supporting Constraint Satisfaction Problems (CSP),
Linear Programming (LP), and Goal Programming (GP).

Classes:
    OXCSPProblem: Base class for constraint satisfaction problems with variables,
        constraints, and special constraints.
    OXLPProblem: Linear programming problem extending CSP with an objective function.
    OXGPProblem: Goal programming problem extending LP with goal constraints and
        deviation variables.
    SpecialConstraintType: Enumeration of special constraint types for non-linear
        operations.
    ObjectiveType: Enumeration of objective types (minimize/maximize).

Functions:
    _create_multiplicative_equality_constraint: Creates multiplication constraints.
    _create_division_or_modulus_equality_constraint: Creates division/modulo constraints.
    _create_summation_equality_constraint: Creates summation constraints.
    _create_conditional_constraint: Creates conditional logic constraints.

Examples:
    >>> from problem import OXLPProblem, ObjectiveType, SpecialConstraintType
    >>> from constraints import RelationalOperators
    >>> 
    >>> # Create a linear programming problem
    >>> problem = OXLPProblem()
    >>> problem.create_decision_variable("x", lower_bound=0, upper_bound=10)
    >>> problem.create_decision_variable("y", lower_bound=0, upper_bound=10)
    >>> 
    >>> # Add a constraint: x + y <= 15
    >>> problem.create_constraint(
    ...     variables=[problem.variables[0].id, problem.variables[1].id],
    ...     weights=[1, 1],
    ...     operator=RelationalOperators.LESS_THAN_EQUAL,
    ...     value=15
    ... )
    >>> 
    >>> # Set objective function: maximize 3x + 2y
    >>> problem.create_objective_function(
    ...     variables=[problem.variables[0].id, problem.variables[1].id],
    ...     weights=[3, 2],
    ...     objective_type=ObjectiveType.MAXIMIZE
    ... )
    >>> 
    >>> # Create a special constraint: z = x * y
    >>> problem.create_special_constraint(
    ...     constraint_type=SpecialConstraintType.MultiplicativeEquality,
    ...     input_variables=[problem.variables[0], problem.variables[1]]
    ... )

The problem hierarchy allows for progressive complexity:
- CSP: Variables and constraints only
- LP: Adds objective function optimization
- GP: Adds goal constraints with deviation variables for multi-objective optimization

See Also:
    :mod:`constraints`: Constraint and expression classes.
    :mod:`variables`: Variable and variable set classes.
    :mod:`data`: Data management classes.
"""

from .OXProblem import (
    OXCSPProblem,
    OXLPProblem,
    OXGPProblem,
    SpecialConstraintType,
    ObjectiveType
)