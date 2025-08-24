import functools
import math
from decimal import Decimal
from fractions import Fraction

from utilities.DynamicValue import DynamicFloat


@functools.lru_cache(maxsize=1024)
def calculate_fraction(value: float | Decimal | int| DynamicFloat) -> Fraction:
    """
    Convert a numeric value to its fractional representation using the mediant method.

    This function converts floating-point numbers to exact fractional representations
    using a binary search approach with mediants. The mediant of two fractions a/b and c/d
    is (a+c)/(b+d), which provides an efficient way to find rational approximations.

    The function handles edge cases where the value is already an integer and uses
    caching to improve performance for repeated calculations.

    Args:
        value (float | Decimal | int): The numeric value to convert to a fraction.
                                     Can be a floating-point number, Decimal, or integer.

    Returns:
        Fraction: The exact fractional representation of the input value.
                 For integers, returns Fraction(value, 1).
                 For floating-point numbers, returns the closest rational approximation.

    Note:
        - Uses LRU cache with maxsize=1024 for performance optimization
        - The mediant method ensures finding exact representations for most decimal values
        - Integer values are handled as a special case for efficiency
        - The algorithm converges when math.isclose() indicates sufficient precision

    Example:
        .. code-block:: python

            # Convert decimal to fraction
            frac1 = calculate_fraction(0.5)  # Returns Fraction(1, 2)
            frac2 = calculate_fraction(0.25) # Returns Fraction(1, 4)
            frac3 = calculate_fraction(2.0)  # Returns Fraction(2, 1)

            # Works with Decimal and int types
            from decimal import Decimal
            frac4 = calculate_fraction(Decimal('0.125'))  # Returns Fraction(1, 8)
            frac5 = calculate_fraction(5)                 # Returns Fraction(5, 1)
    """
    if isinstance(value, DynamicFloat):
        value = value.value
    if int(math.ceil(value)) == int(math.floor(value)):
        return Fraction(math.ceil(value), 1)
    value = float(value)
    ub = Fraction(math.ceil(value), 1)
    lb = Fraction(math.floor(value), 1)
    mediant = Fraction(ub.numerator + lb.numerator, ub.denominator + lb.denominator)
    while not math.isclose(mediant, value):
        if mediant < value:
            lb = mediant
        else:
            ub = mediant
        mediant = Fraction(ub.numerator + lb.numerator, ub.denominator + lb.denominator)
    return mediant
