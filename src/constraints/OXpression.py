"""
Mathematical Expression Module for OptiX Optimization Framework
================================================================

This module provides classes and utilities for representing and manipulating
mathematical expressions in optimization problems. It implements linear
combinations of variables with precise arithmetic handling for coefficients.

The module serves as a foundation for constraint and objective function
definitions, providing robust handling of variable coefficients through
fraction-based arithmetic to avoid floating-point precision issues.

Classes:
    OXpression: Mathematical expression representing linear combinations of variables

Functions:
    get_integer_numerator_and_denominators: Utility for converting floating-point
        coefficients to integer values with common denominators

Key Features:
    - UUID-based variable referencing for serialization compatibility
    - Fraction-based arithmetic for precise coefficient handling
    - Automatic conversion between floating-point and integer representations
    - Support for iterating over variable-coefficient pairs
    - Integration with the OptiX constraint and objective systems

Module Dependencies:
    - math: For mathematical operations (LCM calculation)
    - dataclasses: For structured expression definitions
    - decimal: For precise decimal arithmetic
    - fractions: For rational number arithmetic
    - uuid: For variable identification
    - base: For core OptiX object system integration

Example:
    Creating and manipulating mathematical expressions:

    .. code-block:: python

        from constraints import OXpression
        from variables import OXVariable
        import uuid
        
        # Create variables
        x = OXVariable(name="x", lower_bound=0)
        y = OXVariable(name="y", lower_bound=0)
        z = OXVariable(name="z", lower_bound=0)
        
        # Create expression: 2.5x + 1.5y + 3z
        expr = OXpression(
            variables=[x.id, y.id, z.id],
            weights=[2.5, 1.5, 3.0]
        )
        
        # Access expression properties
        print(f"Number of variables: {expr.number_of_variables}")  # 3
        print(f"Integer weights: {expr.integer_weights}")  # [5, 3, 6]
        print(f"Common denominator: {expr.integer_denominator}")  # 2
        
        # Iterate over variable-weight pairs
        for var_id, weight in expr:
            print(f"Variable {var_id}: coefficient {weight}")
"""

import math
from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from uuid import UUID

from ..base import OXObject


def get_integer_numerator_and_denominators(numbers: list[float | int]) -> tuple[int, list[int]]:
    """Convert a list of floating-point or integer weights to integer values.

    This function finds a common denominator for all the numbers and returns
    the integer numerators and the common denominator.

    Args:
        numbers (list[float | int]): The list of numbers to convert.

    Returns:
        tuple[int, list[int]]: A tuple containing the common denominator and
            a list of integer numerators.

    Examples:
        >>> get_integer_numerator_and_denominators([0.5, 1.5, 2])
        (2, [1, 3, 4])
    """
    fractional_weights = [Fraction(Decimal(str(w))) if not isinstance(w, Fraction) else w for w in numbers]
    denominators = [fw.denominator for fw in fractional_weights]
    numerator = [fw.numerator for fw in fractional_weights]
    common_multiple = math.lcm(*denominators)
    factors = [common_multiple // n for n in denominators]
    numerator = [n * f for n, f in zip(numerator, factors)]
    return common_multiple, numerator


@dataclass
class OXpression(OXObject):
    """A mathematical expression in an optimization problem.

    An expression represents a linear combination of variables, such as "2x + 3y".
    It is used as the left-hand side of constraints and as the objective function.

    Attributes:
        variables (list[UUID]): The list of variable IDs in the expression.
        weights (list[float | int]): The list of coefficients for each variable.

    Examples:
        >>> from uuid import UUID
        >>> var1_id = UUID('12345678-1234-5678-1234-567812345678')
        >>> var2_id = UUID('87654321-4321-8765-4321-876543210987')
        >>> expr = OXpression(variables=[var1_id, var2_id], weights=[2, 3])
        >>> print(expr.number_of_variables)
        2
        >>> print(expr.integer_weights)
        [2, 3]

    Note:
        The variables are stored by their UUIDs rather than direct references,
        which allows for serialization and deserialization of expressions.
    """
    variables: list[UUID] = field(default_factory=list)
    weights: list[float | int | Fraction] = field(default_factory=list)

    @property
    def number_of_variables(self) -> int:
        """Get the number of variables in the expression.

        Returns:
            int: The number of variables.
        """
        return len(self.variables)

    @property
    def integer_weights(self) -> list[int]:
        """Get the weights as integer values.

        This property converts the weights to integer values by finding a common
        denominator. This is useful for solvers that require integer coefficients.

        Returns:
            list[int]: The weights as integer values.

        See Also:
            :func:`get_integer_numerator_and_denominators`
        """
        return get_integer_numerator_and_denominators(self.weights)[1]

    @property
    def integer_denominator(self) -> int:
        """Get the common denominator for the integer weights.

        This property returns the common denominator used to convert the weights
        to integer values. This is useful for solvers that require integer coefficients.

        Returns:
            int: The common denominator.

        See Also:
            :func:`get_integer_numerator_and_denominators`
        """
        return get_integer_numerator_and_denominators(self.weights)[0]

    def __iter__(self):
        """Return an iterator over (variable, weight) pairs.

        Returns:
            iterator: An iterator over (variable, weight) pairs.

        Examples:
            >>> for var_id, weight in expr:
            ...     print(f"Variable {var_id}: {weight}")
            Variable 12345678-1234-5678-1234-567812345678: 2
            Variable 87654321-4321-8765-4321-876543210987: 3
        """
        return iter(zip(self.variables, self.weights))
