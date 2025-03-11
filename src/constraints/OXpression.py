import math
from dataclasses import dataclass, field
from fractions import Fraction
from functools import lru_cache

from uuid import UUID

from base import OXObject


@lru_cache
def get_integer_numerator_and_denominators(numbers: list[float | int]) -> tuple[int, list[int]]:
    fractional_weights = [Fraction(w) for w in numbers]
    denominators = [fw.denominator for fw in fractional_weights]
    numerator = [fw.numerator for fw in fractional_weights]
    common_multiple = math.lcm(*denominators)
    factors = [common_multiple // n for n in denominators]
    numerator = [n * f for n, f in zip(numerator, factors)]
    return common_multiple, numerator


@dataclass
class OXpression(OXObject):
    variables: list[UUID] = field(default_factory=list)
    weights: list[float | int] = field(default_factory=list)

    @property
    def number_of_variables(self) -> int:
        return len(self.variables)

    @property
    def integer_weights(self) -> list[int]:
        return get_integer_numerator_and_denominators(self.weights)[1]

    @property
    def integer_denominator(self) -> int:
        return get_integer_numerator_and_denominators(self.weights)[0]

    def __iter__(self):
        return iter(zip(self.variables, self.weights))
