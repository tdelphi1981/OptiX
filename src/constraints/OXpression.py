import math
from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache
from uuid import UUID

from base import OXObject


@lru_cache
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
    fractional_weights = [Fraction(w) for w in numbers]
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
    weights: list[float | int] = field(default_factory=list)

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
