"""
Constraints Package for OptiX Optimization Framework
=====================================================

This package provides comprehensive constraint modeling capabilities for mathematical
optimization problems. It implements linear constraints, goal programming constraints,
special non-linear constraints, and mathematical expression handling for the OptiX
optimization framework.

The package is organized around the following key components:

Architecture:
    - **Linear Constraints**: Standard constraint definitions with relational operators
    - **Goal Programming**: Specialized constraints with deviation variables for multi-objective optimization
    - **Special Constraints**: Non-linear and complex mathematical relationships
    - **Expression System**: Mathematical expression handling with precise arithmetic
    - **Container Management**: Type-safe collections for organizing constraint sets

Key Features:
    - Support for all standard relational operators (>, >=, =, <, <=)
    - Goal programming with positive and negative deviation variables
    - Non-linear constraints for multiplication, division, modulo, and conditional logic
    - Fraction-based arithmetic for precise coefficient handling
    - UUID-based variable referencing for serialization compatibility
    - Type-safe constraint collections with metadata querying

Constraint Types Covered:
    - **Linear Constraints**: Standard mathematical relationships between variables
    - **Goal Constraints**: Multi-objective optimization with deviation minimization
    - **Special Constraints**: Non-linear operations (multiplication, division, modulo)
    - **Conditional Constraints**: Logical implications and conditional relationships
    - **Expression System**: Linear combinations with precise coefficient handling

Usage:
    Import specific constraint classes and utilities as needed:

    .. code-block:: python

        from constraints import (
            OXConstraint, OXGoalConstraint, OXConstraintSet,
            OXpression, RelationalOperators,
            OXMultiplicativeEqualityConstraint
        )
        from variables import OXVariable
        
        # Create variables
        x = OXVariable(name="x", lower_bound=0, upper_bound=100)
        y = OXVariable(name="y", lower_bound=0, upper_bound=100)
        
        # Create linear constraint: 2x + 3y <= 50
        expr = OXpression(variables=[x.id, y.id], weights=[2, 3])
        constraint = OXConstraint(
            expression=expr,
            relational_operator=RelationalOperators.LESS_THAN_EQUAL,
            rhs=50,
            name="Resource constraint"
        )
        
        # Convert to goal constraint for goal programming
        goal_constraint = constraint.to_goal()

Notes:
    - All constraints use UUID-based variable references for serialization
    - Fraction arithmetic ensures precise coefficient handling
    - Special constraints require constraint programming solvers
    - Goal programming enables multi-objective optimization scenarios
"""

from .OXConstraint import OXConstraint, OXGoalConstraint, RelationalOperators
from .OXConstraintSet import OXConstraintSet
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

__all__ = [
    # Base constraint classes
    "OXConstraint",
    "OXGoalConstraint", 
    "RelationalOperators",
    
    # Constraint management
    "OXConstraintSet",
    
    # Mathematical expressions
    "OXpression",
    "get_integer_numerator_and_denominators",
    
    # Special constraints
    "OXSpecialConstraint",
    "OXNonLinearEqualityConstraint",
    "OXMultiplicativeEqualityConstraint",
    "OXDivisionEqualityConstraint",
    "OXModuloEqualityConstraint",
    "OXSummationEqualityConstraint",
    "OXConditionalConstraint",
]