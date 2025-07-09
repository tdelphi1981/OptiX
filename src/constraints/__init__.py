"""Constraints package for the OptiX optimization framework.

This package contains classes for representing constraints in optimization problems.
It provides support for linear constraints, goal constraints for goal programming,
mathematical expressions, and special non-linear constraints.

Classes:
    OXConstraint: Standard linear constraint with left-hand side expression and right-hand side value.
    OXGoalConstraint: Goal constraint for goal programming with deviation variables.
    RelationalOperators: Enumeration of comparison operators (>, >=, =, <, <=).
    OXpression: Mathematical expression representing linear combinations of variables.
    OXSpecialConstraint: Base class for non-linear and special constraints.
    OXNonLinearEqualityConstraint: Base class for non-linear equality constraints.
    OXMultiplicativeEqualityConstraint: Constraint for variable multiplication.
    OXDivisionEqualityConstraint: Constraint for integer division operations.
    OXModuloEqualityConstraint: Constraint for modulo operations.
    OXSummationEqualityConstraint: Constraint for variable summation.
    OXConditionalConstraint: Constraint for conditional logic.

Functions:
    get_integer_numerator_and_denominators: Utility function to convert floating-point
        weights to integer values with a common denominator.

Examples:
    >>> from constraints import OXConstraint, OXpression, RelationalOperators
    >>> # Create a linear constraint: 2x + 3y <= 10
    >>> expr = OXpression(variables=[x.id, y.id], weights=[2, 3])
    >>> constraint = OXConstraint(
    ...     expression=expr,
    ...     relational_operator=RelationalOperators.LESS_THAN_EQUAL,
    ...     rhs=10
    ... )
    
    >>> # Create a goal constraint for goal programming
    >>> goal = constraint.to_goal()
    >>> print(goal.negative_deviation_variable.desired)
    True
"""

from .OXConstraint import OXConstraint, OXGoalConstraint, RelationalOperators
from .OXpression import OXpression, get_integer_numerator_and_denominators
from .OXSpecialConstraints import (
    OXSpecialConstraint,
    OXNonLinearEqualityConstraint,
    OXMultiplicativeEqualityConstraint,
    OXDivisionEqualityConstraint,
    OXModuloEqualityConstraint,
    OXSummationEqualityConstraint,
    OXConditionalConstraint
)