"""
Constraint Module for OptiX Optimization Framework
===================================================

This module provides constraint classes for representing and managing linear constraints
in optimization problems. It implements standard linear constraints and goal programming
constraints with support for multiple relational operators and deviation variables.

The module is a core component of the OptiX framework's constraint system, enabling
the definition of mathematical relationships between variables that must be satisfied
by the optimization solver.

Classes:
    RelationalOperators: Enumeration of comparison operators (>, >=, =, <, <=)
    OXConstraint: Standard linear constraint with expression and relational operator
    OXGoalConstraint: Goal programming constraint with positive and negative deviation variables

Key Features:
    - Support for all standard relational operators
    - Automatic conversion from regular constraints to goal constraints
    - Fraction-based arithmetic for precise coefficient handling
    - Integration with OXpression for complex mathematical expressions
    - Deviation variable management for goal programming

Module Dependencies:
    - dataclasses: For structured constraint definitions
    - enum: For relational operator enumeration
    - fractions: For precise arithmetic operations
    - base: For core OptiX object system
    - constraints.OXpression: For mathematical expression handling
    - variables.OXDeviationVar: For goal programming deviation variables

Example:
    Basic constraint creation and usage:

    .. code-block:: python

        from constraints import OXConstraint, OXpression, RelationalOperators
        from variables import OXVariable
        
        # Create variables
        x = OXVariable(name="x", lower_bound=0)
        y = OXVariable(name="y", lower_bound=0)
        
        # Create expression: 2x + 3y
        expr = OXpression(variables=[x.id, y.id], weights=[2, 3])
        
        # Create constraint: 2x + 3y <= 10
        constraint = OXConstraint(
            expression=expr,
            relational_operator=RelationalOperators.LESS_THAN_EQUAL,
            rhs=10,
            name="Capacity constraint"
        )
        
        # Convert to goal constraint for goal programming
        goal_constraint = constraint.to_goal()
        print(goal_constraint.negative_deviation_variable.desired)  # True
"""

from dataclasses import dataclass, field
from enum import StrEnum
from fractions import Fraction

from ..base import OXObject, OXception
from .OXpression import OXpression
from ..variables.OXDeviationVar import OXDeviationVar


class RelationalOperators(StrEnum):
    """Enumeration of relational operators for constraints.

    These operators define the relationship between the left-hand side (expression)
    and right-hand side (rhs) of a constraint.

    Attributes:
        GREATER_THAN (str): The ">" operator.
        GREATER_THAN_EQUAL (str): The ">=" operator.
        EQUAL (str): The "=" operator.
        LESS_THAN (str): The "<" operator.
        LESS_THAN_EQUAL (str): The "<=" operator.
    """
    GREATER_THAN = ">"
    GREATER_THAN_EQUAL = ">="
    EQUAL = "="
    LESS_THAN = "<"
    LESS_THAN_EQUAL = "<="


@dataclass
class OXConstraint(OXObject):
    """A constraint in an optimization problem.

    A constraint represents a relationship between an expression and a value,
    such as "2x + 3y <= 10".

    Attributes:
        expression (OXpression): The left-hand side of the constraint.
        relational_operator (RelationalOperators): The operator (>, >=, =, <, <=).
        rhs (float | int): The right-hand side value.
        name (str): A descriptive name for the constraint.

    Examples:
        >>> from constraints.OXpression import OXpression
        >>> expr = OXpression(variables=[var1.id, var2.id], weights=[2, 3])
        >>> constraint = OXConstraint(
        ...     expression=expr,
        ...     relational_operator=RelationalOperators.LESS_THAN_EQUAL,
        ...     rhs=10,
        ...     name="Capacity constraint"
        ... )
        >>> print(constraint)
        constraints.OXConstraint(12345678-1234-5678-1234-567812345678)
    """
    expression: OXpression = field(default_factory=OXpression)
    relational_operator: RelationalOperators = RelationalOperators.EQUAL
    rhs: float | int = 0
    name: str = ""

    def reverse(self):
        """Reverse the relational operator of the constraint.

        This method changes the relational operator to its opposite:
        - GREATER_THAN becomes LESS_THAN
        - GREATER_THAN_EQUAL becomes LESS_THAN_EQUAL
        - EQUAL remains EQUAL
        - LESS_THAN becomes GREATER_THAN
        - LESS_THAN_EQUAL becomes GREATER_THAN_EQUAL

        Returns:
            OXConstraint: A new constraint with the reversed operator.
        """
        if self.relational_operator == RelationalOperators.EQUAL:
            raise OXception("Cannot reverse an equality constraint.")
        reversed_operator = {
            RelationalOperators.GREATER_THAN: RelationalOperators.LESS_THAN_EQUAL,
            RelationalOperators.GREATER_THAN_EQUAL: RelationalOperators.LESS_THAN,
            RelationalOperators.LESS_THAN: RelationalOperators.GREATER_THAN_EQUAL,
            RelationalOperators.LESS_THAN_EQUAL: RelationalOperators.GREATER_THAN
        }[self.relational_operator]

        return OXConstraint(
            expression=self.expression,
            relational_operator=reversed_operator,
            rhs=self.rhs,
            name=f"Inverse of {self.name}"
        )

    @property
    def rhs_numerator(self):
        """Get the numerator of the right-hand side as a fraction.

        Returns:
            int: The numerator of the right-hand side.
        """
        return Fraction(self.rhs).numerator

    @property
    def rhs_denominator(self):
        """Get the denominator of the right-hand side as a fraction.

        Returns:
            int: The denominator of the right-hand side.
        """
        return Fraction(self.rhs).denominator

    def to_goal(self, upper_bound: int | float | Fraction = 100) -> "OXGoalConstraint":
        """Convert this constraint to a goal constraint for goal programming.

        The conversion sets the relational operator to EQUAL and sets the
        desired deviation variables based on the original operator.

        Returns:
            OXGoalConstraint: A new goal constraint based on this constraint.

        See Also:
            :class:`OXGoalConstraint`
        """
        result = OXGoalConstraint()
        result.expression = self.expression
        result.relational_operator = RelationalOperators.EQUAL
        result.rhs = self.rhs
        result.name = self.name
        result.positive_deviation_variable.name = f"Positive deviation of {self.name}"
        result.negative_deviation_variable.name = f"Negative deviation of {self.name}"
        if self.relational_operator in [RelationalOperators.LESS_THAN, RelationalOperators.LESS_THAN_EQUAL]:
            result.negative_deviation_variable.desired = True
            result.negative_deviation_variable.upper_bound = upper_bound
            result.positive_deviation_variable.upper_bound = upper_bound
        elif self.relational_operator in [RelationalOperators.GREATER_THAN, RelationalOperators.GREATER_THAN_EQUAL]:
            result.positive_deviation_variable.desired = True
            result.positive_deviation_variable.upper_bound = upper_bound
            result.negative_deviation_variable.upper_bound = upper_bound
        return result


@dataclass
class OXGoalConstraint(OXConstraint):
    """A goal constraint for goal programming.

    A goal constraint extends a regular constraint by adding deviation variables
    that measure how much the constraint is violated. In goal programming, the
    objective is typically to minimize undesired deviations.

    Attributes:
        positive_deviation_variable (OXDeviationVar): The variable representing
            positive deviation from the goal.
        negative_deviation_variable (OXDeviationVar): The variable representing
            negative deviation from the goal.

    Examples:
        >>> goal = constraint.to_goal()
        >>> print(goal.positive_deviation_variable.desired)
        False
        >>> print(goal.negative_deviation_variable.desired)
        True

    See Also:
        :class:`OXConstraint`
        :class:`variables.OXDeviationVar.OXDeviationVar`
    """
    positive_deviation_variable: OXDeviationVar = field(default_factory=OXDeviationVar)
    negative_deviation_variable: OXDeviationVar = field(default_factory=OXDeviationVar)

    @property
    def desired_variables(self) -> list[OXDeviationVar]:
        """Get the list of desired deviation variables.

        Returns:
            list[OXDeviationVar]: A list of deviation variables marked as desired.
        """
        result = []
        if self.positive_deviation_variable.desired:
            result.append(self.positive_deviation_variable)
        if self.negative_deviation_variable.desired:
            result.append(self.negative_deviation_variable)
        return result

    @property
    def undesired_variables(self) -> list[OXDeviationVar]:
        """Get the list of undesired deviation variables.

        Returns:
            list[OXDeviationVar]: A list of deviation variables not marked as desired.
        """
        result = []
        if not self.positive_deviation_variable.desired:
            result.append(self.positive_deviation_variable)
        if not self.negative_deviation_variable.desired:
            result.append(self.negative_deviation_variable)
        return result
