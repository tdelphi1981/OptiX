"""
Special Constraints Module for OptiX Optimization Framework
============================================================

This module provides specialized constraint classes for handling non-linear and
complex mathematical relationships in optimization problems. These constraints
extend beyond standard linear programming to support constraint programming
and mixed-integer programming scenarios.

The module implements various types of special constraints that cannot be expressed
as simple linear relationships, including multiplicative operations, division,
modulo arithmetic, summation operations, and conditional logic.

Classes:
    OXSpecialConstraint: Base class for all special constraint types
    OXNonLinearEqualityConstraint: Base class for non-linear equality constraints
    OXMultiplicativeEqualityConstraint: Constraint for variable multiplication operations
    OXDivisionEqualityConstraint: Constraint for integer division operations
    OXModuloEqualityConstraint: Constraint for modulo arithmetic operations
    OXSummationEqualityConstraint: Constraint for variable summation operations
    OXConditionalConstraint: Constraint for conditional logic and implications

Key Features:
    - Support for non-linear mathematical operations
    - UUID-based variable referencing for serialization compatibility
    - Integration with constraint programming solvers
    - Conditional logic and implication modeling
    - Type-safe constraint definitions with dataclass structure

Module Dependencies:
    - dataclasses: For structured constraint definitions
    - uuid: For variable identification and referencing
    - base: For core OptiX object system integration

Example:
    Creating and using special constraints for complex relationships:

    .. code-block:: python

        from constraints import (
            OXMultiplicativeEqualityConstraint,
            OXDivisionEqualityConstraint,
            OXConditionalConstraint
        )
        from variables import OXVariable
        
        # Create variables
        x = OXVariable(name="x", lower_bound=0, upper_bound=100)
        y = OXVariable(name="y", lower_bound=0, upper_bound=100)
        z = OXVariable(name="z", lower_bound=0, upper_bound=10000)
        quotient = OXVariable(name="quotient", lower_bound=0, upper_bound=50)
        
        # Create multiplication constraint: z = x * y
        mult_constraint = OXMultiplicativeEqualityConstraint(
            input_variables=[x.id, y.id],
            output_variable=z.id
        )
        
        # Create division constraint: quotient = x // 2
        div_constraint = OXDivisionEqualityConstraint(
            input_variable=x.id,
            denominator=2,
            output_variable=quotient.id
        )
        
        # These constraints would be added to a constraint programming problem
        # for solving with appropriate solvers like OR-Tools CP-SAT
"""

from dataclasses import dataclass, field
from uuid import UUID

from base import OXObject


@dataclass
class OXSpecialConstraint(OXObject):
    """Base class for special constraints in optimization problems.

    Special constraints are non-linear constraints that cannot be expressed
    as simple linear relationships. They require special handling by solvers
    and often involve complex relationships between variables.

    This class serves as a base for all special constraint types including
    multiplicative, division, modulo, summation, and conditional constraints.

    See Also:
        :class:`OXNonLinearEqualityConstraint`
        :class:`OXMultiplicativeEqualityConstraint`
        :class:`OXDivisionEqualityConstraint`
        :class:`OXModuloEqualityConstraint`
        :class:`OXSummationEqualityConstraint`
        :class:`OXConditionalConstraint`
    """
    pass


@dataclass
class OXNonLinearEqualityConstraint(OXSpecialConstraint):
    """Base class for non-linear equality constraints.

    Non-linear equality constraints represent relationships that cannot be
    expressed as linear combinations of variables. They typically have the
    form f(x1, x2, ..., xn) = output_variable, where f is a non-linear function.

    Attributes:
        output_variable (UUID): The UUID of the variable that stores the result
            of the non-linear operation.

    Examples:
        This is a base class and should not be instantiated directly.
        Use specific subclasses like OXMultiplicativeEqualityConstraint.

    See Also:
        :class:`OXMultiplicativeEqualityConstraint`
        :class:`OXDivisionEqualityConstraint`
        :class:`OXModuloEqualityConstraint`
    """
    output_variable: UUID = field(default_factory=UUID)


@dataclass
class OXMultiplicativeEqualityConstraint(OXNonLinearEqualityConstraint):
    """A constraint representing multiplication of variables.

    This constraint enforces that the output variable equals the product
    of all input variables: output_variable = input_variable_1 * input_variable_2 * ... * input_variable_n

    Attributes:
        input_variables (list[UUID]): The list of variable UUIDs to multiply.
        output_variable (UUID): The UUID of the variable that stores the product.
            Inherited from OXNonLinearEqualityConstraint.

    Examples:
        >>> # Create a constraint: z = x * y
        >>> constraint = OXMultiplicativeEqualityConstraint(
        ...     input_variables=[x.id, y.id],
        ...     output_variable=z.id
        ... )

    Note:
        This constraint is typically handled by constraint programming solvers
        that support non-linear operations.
    """
    input_variables: list[UUID] = field(default_factory=list)


@dataclass
class OXDivisionEqualityConstraint(OXNonLinearEqualityConstraint):
    """A constraint representing integer division of a variable.

    This constraint enforces that the output variable equals the integer division
    of the input variable by the denominator: output_variable = input_variable // denominator

    Attributes:
        input_variable (UUID): The UUID of the variable to divide.
        denominator (int): The divisor for the division operation.
        output_variable (UUID): The UUID of the variable that stores the quotient.
            Inherited from OXNonLinearEqualityConstraint.

    Examples:
        >>> # Create a constraint: z = x // 3
        >>> constraint = OXDivisionEqualityConstraint(
        ...     input_variable=x.id,
        ...     denominator=3,
        ...     output_variable=z.id
        ... )

    Note:
        This constraint performs integer division (floor division), not
        floating-point division.
    """
    input_variable: UUID = field(default_factory=UUID)
    denominator: int = 1


@dataclass
class OXModuloEqualityConstraint(OXNonLinearEqualityConstraint):
    """A constraint representing modulo operation on a variable.

    This constraint enforces that the output variable equals the remainder
    of the input variable divided by the denominator: output_variable = input_variable % denominator

    Attributes:
        input_variable (UUID): The UUID of the variable to apply modulo to.
        denominator (int): The divisor for the modulo operation.
        output_variable (UUID): The UUID of the variable that stores the remainder.
            Inherited from OXNonLinearEqualityConstraint.

    Examples:
        >>> # Create a constraint: z = x % 5
        >>> constraint = OXModuloEqualityConstraint(
        ...     input_variable=x.id,
        ...     denominator=5,
        ...     output_variable=z.id
        ... )

    Note:
        The result is always non-negative and less than the denominator.
    """
    input_variable: UUID = field(default_factory=UUID)
    denominator: int = 1


@dataclass
class OXSummationEqualityConstraint(OXSpecialConstraint):
    """A constraint representing summation of variables.

    This constraint enforces that the output variable equals the sum
    of all input variables: output_variable = input_variable_1 + input_variable_2 + ... + input_variable_n

    Attributes:
        input_variables (list[UUID]): The list of variable UUIDs to sum.
        output_variable (UUID): The UUID of the variable that stores the sum.

    Examples:
        >>> # Create a constraint: z = x + y + w
        >>> constraint = OXSummationEqualityConstraint(
        ...     input_variables=[x.id, y.id, w.id],
        ...     output_variable=z.id
        ... )

    Note:
        While this could be expressed as a linear constraint, it's included
        as a special constraint for consistency and solver optimization.
    """
    input_variables: list[UUID] = field(default_factory=list)
    output_variable: UUID = field(default_factory=UUID)


@dataclass
class OXConditionalConstraint(OXSpecialConstraint):
    """A constraint representing conditional logic.

    This constraint enforces different constraints based on the value of an indicator variable.
    If the indicator variable is true, constraint_if_true is enforced; otherwise,
    constraint_if_false is enforced.

    Attributes:
        indicator_variable (UUID): The UUID of the boolean variable that determines
            which constraint to enforce.
        input_constraint (UUID): The UUID of the base constraint to evaluate.
        constraint_if_true (UUID): The UUID of the constraint to enforce if
            the indicator variable is true.
        constraint_if_false (UUID): The UUID of the constraint to enforce if
            the indicator variable is false.

    Examples:
        >>> # Create a conditional constraint: if flag then x >= 5 else x <= 3
        >>> constraint = OXConditionalConstraint(
        ...     indicator_variable=flag.id,
        ...     input_constraint=base_constraint.id,
        ...     constraint_if_true=upper_bound_constraint.id,
        ...     constraint_if_false=lower_bound_constraint.id
        ... )

    Note:
        This constraint is used for modeling logical implications and
        conditional relationships in optimization problems.
    """
    indicator_variable: UUID = field(default_factory=UUID)
    input_constraint: UUID = field(default_factory=UUID)
    constraint_if_true: UUID = field(default_factory=UUID)
    constraint_if_false: UUID = field(default_factory=UUID)
